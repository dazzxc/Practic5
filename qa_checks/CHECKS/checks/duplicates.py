"""проверка 2: дубликаты по хешам"""

import numpy as np
import pandas as pd

from checks.issue import get_severity, has_value, make_issue


class SeenValues:
    """хеши увиденного"""

    def __init__(self):
        self.hashes = np.array([], dtype=np.uint64)

    def find_repeats(self, new_hashes):
        """видели ли хеш раньше"""
        new_hashes = np.asarray(new_hashes, dtype=np.uint64)

        # повторы в куске
        repeat_in_chunk = pd.Series(new_hashes).duplicated(keep="first").to_numpy()

        # повторы с прошлыми
        repeat_before = np.isin(new_hashes, self.hashes, assume_unique=False)

        # запоминаем
        self.hashes = np.union1d(self.hashes, new_hashes)

        return repeat_in_chunk | repeat_before


class DuplicateChecker:
    """дубли по всему файлу"""

    def __init__(self, key_columns=None):
        self.key_columns = key_columns or []

        self.seen_rows = SeenValues()
        self.seen_keys = {col: SeenValues() for col in self.key_columns}

        self.row_samples = []   # 5 примеров
        self.row_count = 0
        self.key_samples = {col: [] for col in self.key_columns}
        self.key_count = {col: 0 for col in self.key_columns}

    def add_chunk(self, chunk):
        """очередной кусок"""
        self._check_full_rows(chunk)
        for column in self.key_columns:
            if column in chunk.columns:
                self._check_key(chunk, column)

    def _check_full_rows(self, chunk):
        # хеш строки; str, чтобы 7 == "7"
        hashes = pd.util.hash_pandas_object(chunk.astype(str), index=False)
        is_repeat = self.seen_rows.find_repeats(hashes)

        bad_rows = chunk.index[is_repeat]
        self.row_count += len(bad_rows)
        self.row_samples = (self.row_samples + bad_rows[:5].tolist())[:5]

    def _check_key(self, chunk, column):
        filled = has_value(chunk[column])  # без пустых ключей
        values = chunk.loc[filled, column].astype(str).str.strip()
        hashes = pd.util.hash_pandas_object(values, index=False)
        is_repeat = self.seen_keys[column].find_repeats(hashes)

        bad_rows = values.index[is_repeat]
        self.key_count[column] += len(bad_rows)
        self.key_samples[column] = (self.key_samples[column] + bad_rows[:5].tolist())[:5]

    def get_issues(self, total_rows):
        """после чтения файла"""
        issues = []

        if self.row_count:
            issues.append(_issue("duplicate_row", None, self.row_count, self.row_samples,
                                 total_rows, f"Найдено {self.row_count} полностью одинаковых строк"))

        for column in self.key_columns:
            count = self.key_count[column]
            if count:
                issues.append(_issue("duplicate_key", column, count, self.key_samples[column],
                                     total_rows,
                                     f"В колонке '{column}' значения повторяются в {count} строках"))
        return issues


def _issue(issue_type, column, count, samples, total_rows, message):
    """ошибка с полным count"""
    issue = make_issue(issue_type, column, samples, total_rows, message)
    issue["count"] = count
    issue["percent"] = round(count / total_rows * 100, 2) if total_rows else 0
    issue["severity"] = get_severity(issue["percent"])
    return issue


def check_duplicates(df, key_columns=None):
    """таблица в памяти"""
    checker = DuplicateChecker(key_columns)
    checker.add_chunk(df)
    return checker.get_issues(len(df))
