"""
Главные функции модуля.

1) check_file(path, config) - проверяет файл ЛЮБОГО размера, читая его по частям.
   Именно её будет вызывать бэкенд (Человек 1).

2) run_all_checks(df, config) - проверяет маленькую таблицу, которая уже в памяти.

Как работает check_file:
    читаем 15 000 строк -> проверяем -> запоминаем ошибки -> выкидываем строки из памяти
    читаем следующие 15 000 строк -> ...
    в конце складываем ошибки из всех частей в один список.
"""

from checks.consistency import check_consistency
from checks.duplicates import DuplicateChecker
from checks.invalid import check_invalid
from checks.issue import get_severity
from checks.missing import check_missing
from checks.reader import DEFAULT_CHUNK_SIZE, read_in_chunks


class IssueCollector:
    """
    Складывает ошибки из разных частей файла.

    Например, в чанке 1 нашлось 3 пустых email, в чанке 2 - ещё 5.
    Итог: одна проблема "пустой email" с count = 8.
    """

    def __init__(self):
        self.issues = {}  # ключ: (тип, колонка)

    def add(self, chunk_issues):
        for issue in chunk_issues:
            key = (issue["type"], issue["column"])

            if key not in self.issues:
                self.issues[key] = issue
            else:
                saved = self.issues[key]
                saved["count"] += issue["count"]
                # Примеров строк храним не больше 5
                saved["sample_rows"] = (saved["sample_rows"] + issue["sample_rows"])[:5]

    def get_issues(self, total_rows):
        """Пересчитывает процент и серьёзность от ВСЕГО файла, а не от одного чанка."""
        result = []
        for issue in self.issues.values():
            issue["percent"] = round(issue["count"] / total_rows * 100, 2) if total_rows else 0
            issue["severity"] = get_severity(issue["percent"])
            if issue["type"] == "missing":
                issue["message"] = (f"В колонке '{issue['column']}' пусто в "
                                    f"{issue['count']} строках из {total_rows}")
            result.append(issue)
        return result


def check_file(path, config=None, chunk_size=DEFAULT_CHUNK_SIZE, on_progress=None):
    """
    Проверяет файл любого размера.

    path        - путь к .csv, .xlsx или .json
    config      - настройки проверок (см. run.py)
    chunk_size  - сколько строк читать за раз
    on_progress - необязательная функция, которую вызываем после каждого чанка
                  с числом уже проверенных строк (пригодится для прогресс-бара).

    Возвращает словарь: {"total_rows": ..., "columns": [...], "issues": [...]}
    """
    config = config or {}
    collector = IssueCollector()
    duplicates = DuplicateChecker(config.get("key_columns"))

    total_rows = 0
    columns = []

    for chunk in read_in_chunks(path, chunk_size):
        # В JSON у разных записей могут быть разные поля.
        # Если в этой части появилась новая колонка, то во ВСЕХ прошлых строках
        # её не было - это тоже пропуски, их надо посчитать.
        new_columns = [c for c in chunk.columns if c not in columns]
        if new_columns and total_rows > 0:
            collector.add(_missing_in_previous_rows(new_columns, total_rows))
        columns += new_columns

        # Все части приводим к одному набору колонок (чего нет - будет пусто)
        chunk = chunk.reindex(columns=columns)

        # Эти проверки смотрят только на одну строку, поэтому работают по чанку
        collector.add(check_missing(chunk))
        collector.add(check_invalid(chunk, config.get("invalid_rules", {})))
        collector.add(check_consistency(chunk, config.get("consistency_rules", [])))

        # Дубли должны помнить прошлые чанки
        duplicates.add_chunk(chunk)

        total_rows += len(chunk)
        if on_progress:
            on_progress(total_rows)

    issues = collector.get_issues(total_rows) + duplicates.get_issues(total_rows)
    issues.sort(key=_issue_order)

    return {"total_rows": total_rows, "columns": columns, "issues": issues}


def _missing_in_previous_rows(new_columns, rows_before):
    """Пропуски в колонках, которые появились не в первой части файла."""
    issues = []
    for column in new_columns:
        issues.append({
            "type": "missing",
            "column": column,
            "count": rows_before,
            "percent": 0,      # пересчитается в конце
            "severity": "low",  # пересчитается в конце
            "message": "",      # пересчитается в конце
            "sample_rows": list(range(min(5, rows_before))),
        })
    return issues


def run_all_checks(df, config=None):
    """Проверка маленькой таблицы, которая уже целиком в памяти."""
    config = config or {}
    collector = IssueCollector()
    duplicates = DuplicateChecker(config.get("key_columns"))

    collector.add(check_missing(df))
    collector.add(check_invalid(df, config.get("invalid_rules", {})))
    collector.add(check_consistency(df, config.get("consistency_rules", [])))
    duplicates.add_chunk(df)

    issues = collector.get_issues(len(df)) + duplicates.get_issues(len(df))
    issues.sort(key=_issue_order)
    return issues


# Порядок вывода: сначала пропуски, потом дубли, потом остальное
_ORDER = ["missing", "duplicate_row", "duplicate_key", "wrong_type", "out_of_range",
          "wrong_format", "wrong_date", "not_allowed", "inconsistent"]


def _issue_order(issue):
    return _ORDER.index(issue["type"]) if issue["type"] in _ORDER else len(_ORDER)
