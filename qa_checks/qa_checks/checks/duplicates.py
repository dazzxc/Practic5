"""
Проверка 2: дубликаты.

- полные дубли: строки, где совпадает всё;
- дубли по ключу: например, два клиента с одинаковым id.

Сложность с чанками: строка в чанке №1 и её копия в чанке №5 должны найтись.
Поэтому проверка "помнит", какие строки уже видела.

Чтобы не хранить в памяти сами строки, храним только их "отпечаток" (хеш):
одно число размером 8 байт на строку. Даже 100 млн строк = примерно 800 МБ.
Отпечатки лежат в отсортированном массиве numpy - так поиск очень быстрый.
"""

import numpy as np
import pandas as pd

from checks.issue import get_severity, has_value, make_issue


class SeenValues:
    """
    "Память" о том, какие значения уже встречались.
    Хранит отпечатки (хеши) в отсортированном массиве.
    """

    def __init__(self):
        self.hashes = np.array([], dtype=np.uint64)

    def find_repeats(self, new_hashes):
        """
        Получает отпечатки нового чанка.
        Возвращает True/False для каждой строки: встречалась ли она раньше
        (в прошлых чанках ИЛИ выше в этом же чанке).
        """
        new_hashes = np.asarray(new_hashes, dtype=np.uint64)

        # 1) Повторы внутри самого чанка
        repeat_in_chunk = pd.Series(new_hashes).duplicated(keep="first").to_numpy()

        # 2) Повторы с прошлыми чанками (быстрый поиск в отсортированном массиве)
        repeat_before = np.isin(new_hashes, self.hashes, assume_unique=False)

        # 3) Запоминаем новые значения
        self.hashes = np.union1d(self.hashes, new_hashes)

        return repeat_in_chunk | repeat_before


class DuplicateChecker:
    """Ищет дубли во всём файле, получая его по частям."""

    def __init__(self, key_columns=None):
        self.key_columns = key_columns or []

        self.seen_rows = SeenValues()
        self.seen_keys = {col: SeenValues() for col in self.key_columns}

        self.row_samples = []   # первые 5 строк-дублей (для примера)
        self.row_count = 0      # сколько всего дублей
        self.key_samples = {col: [] for col in self.key_columns}
        self.key_count = {col: 0 for col in self.key_columns}

    def add_chunk(self, chunk):
        """Проверяет очередную часть файла."""
        self._check_full_rows(chunk)
        for column in self.key_columns:
            if column in chunk.columns:
                self._check_key(chunk, column)

    def _check_full_rows(self, chunk):
        # Превращаем каждую строку в одно число (хеш).
        # astype(str) - чтобы одинаково обрабатывать любые типы данных.
        hashes = pd.util.hash_pandas_object(chunk.astype(str), index=False)
        is_repeat = self.seen_rows.find_repeats(hashes)

        bad_rows = chunk.index[is_repeat]
        self.row_count += len(bad_rows)
        self.row_samples = (self.row_samples + bad_rows[:5].tolist())[:5]

    def _check_key(self, chunk, column):
        filled = has_value(chunk[column])  # пустые ключи дублями не считаем
        values = chunk.loc[filled, column].astype(str).str.strip()
        hashes = pd.util.hash_pandas_object(values, index=False)
        is_repeat = self.seen_keys[column].find_repeats(hashes)

        bad_rows = values.index[is_repeat]
        self.key_count[column] += len(bad_rows)
        self.key_samples[column] = (self.key_samples[column] + bad_rows[:5].tolist())[:5]

    def get_issues(self, total_rows):
        """Вызывается в конце, когда весь файл прочитан."""
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
    """Создаёт Issue с настоящим количеством (в samples только 5 примеров)."""
    issue = make_issue(issue_type, column, samples, total_rows, message)
    issue["count"] = count
    issue["percent"] = round(count / total_rows * 100, 2) if total_rows else 0
    issue["severity"] = get_severity(issue["percent"])
    return issue


def check_duplicates(df, key_columns=None):
    """Простой вариант для маленькой таблицы, которая уже целиком в памяти."""
    checker = DuplicateChecker(key_columns)
    checker.add_chunk(df)
    return checker.get_issues(len(df))
