"""
Тут две главные функции:

check_file(path, config)   - проверяет файл любого размера, читая его кусками.
                             Её вызывает бэкенд.
run_all_checks(df, config) - то же самое для небольшой таблицы, которая уже в памяти.

Если config не передать, правила подберутся сами (см. auto_rules.py).

check_file работает так: берём 15 000 строк, проверяем, запоминаем ошибки,
выкидываем эти строки из памяти и берём следующие. В конце всё складываем.
"""

from checks.auto_rules import suggest_rules
from checks.consistency import check_consistency
from checks.duplicates import DuplicateChecker
from checks.invalid import check_invalid
from checks.issue import CATEGORIES, get_category, get_severity
from checks.missing import check_missing
from checks.reader import DEFAULT_CHUNK_SIZE, read_in_chunks


class IssueCollector:
    """
    Собирает ошибки со всех кусков файла в одну кучу.
    Например, в первом куске 3 пустых email, во втором ещё 5 - в итоге одна ошибка на 8 строк.
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
                # Больше 5 примеров не храним
                saved["sample_rows"] = (saved["sample_rows"] + issue["sample_rows"])[:5]

    def get_issues(self, total_rows):
        """Считаем процент и серьёзность уже от всего файла, а не от одного куска."""
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
    config      - правила проверки; None - подобрать самим
    chunk_size  - сколько строк читать за раз
    on_progress - можно передать функцию, она получит число проверенных строк
                  после каждого куска (удобно для прогресс-бара)

    Что вернёт:
    {
        "total_rows": ...,
        "columns": [...],
        "issues": [...],
        "summary": {"missing": ..., "duplicate": ..., "invalid": ..., "inconsistency": ...},
        "config": {...},       # какие правила использовались
        "auto_rules": True/False,
    }
    """
    auto = config is None
    collector = IssueCollector()
    duplicates = None  # создадим, когда узнаем ключевые колонки

    total_rows = 0
    columns = []

    for chunk in read_in_chunks(path, chunk_size):
        # На первом куске подбираем правила, если их не дали
        if duplicates is None:
            if auto:
                config = suggest_rules(chunk)
            duplicates = DuplicateChecker(config.get("key_columns"))

        # В JSON у записей бывают разные поля. Если колонка появилась только сейчас,
        # значит во всех строках до этого её не было - это тоже пропуски.
        new_columns = [c for c in chunk.columns if c not in columns]
        if new_columns and total_rows > 0:
            collector.add(_missing_in_previous_rows(new_columns, total_rows))
        columns += new_columns

        # Делаем у всех кусков одинаковые колонки (чего нет - будет пусто)
        chunk = chunk.reindex(columns=columns)

        # Этим проверкам хватает одной строки, так что гоняем их по куску
        collector.add(check_missing(chunk))
        collector.add(check_invalid(chunk, config.get("invalid_rules", {})))
        collector.add(check_consistency(chunk, config.get("consistency_rules", [])))

        # А дублям нужно помнить прошлые куски
        duplicates.add_chunk(chunk)

        total_rows += len(chunk)
        if on_progress:
            on_progress(total_rows)

    if duplicates is None:  # файл пустой
        config = config or {}
        duplicates = DuplicateChecker()

    issues = collector.get_issues(total_rows) + duplicates.get_issues(total_rows)
    issues.sort(key=_issue_order)

    return {
        "total_rows": total_rows,
        "columns": columns,
        "issues": issues,
        "summary": make_summary(issues),
        "config": config,
        "auto_rules": auto,
    }


def make_summary(issues):
    """Сколько ошибок в каждой из 4 групп."""
    summary = {category: 0 for category in set(CATEGORIES.values())}
    for issue in issues:
        summary[issue["category"]] += issue["count"]
    return summary


def _missing_in_previous_rows(new_columns, rows_before):
    """Пропуски в колонках, которые появились не с самого начала файла."""
    issues = []
    for column in new_columns:
        issues.append({
            "type": "missing",
            "category": get_category("missing"),
            "column": column,
            "count": rows_before,
            # percent, severity и message посчитаются в конце
            "percent": 0,
            "severity": "low",
            "message": "",
            "sample_rows": list(range(min(5, rows_before))),
        })
    return issues


def run_all_checks(df, config=None):
    """Проверка небольшой таблицы, которая уже в памяти."""
    if config is None:
        config = suggest_rules(df)
    collector = IssueCollector()
    duplicates = DuplicateChecker(config.get("key_columns"))

    collector.add(check_missing(df))
    collector.add(check_invalid(df, config.get("invalid_rules", {})))
    collector.add(check_consistency(df, config.get("consistency_rules", [])))
    duplicates.add_chunk(df)

    issues = collector.get_issues(len(df)) + duplicates.get_issues(len(df))
    issues.sort(key=_issue_order)
    return issues


# В каком порядке выводить ошибки
_ORDER = ["missing", "duplicate_row", "duplicate_key", "wrong_type", "out_of_range",
          "wrong_format", "wrong_date", "not_allowed", "inconsistent"]


def _issue_order(issue):
    return _ORDER.index(issue["type"]) if issue["type"] in _ORDER else len(_ORDER)
