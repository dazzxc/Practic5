"""
Как выглядит одна найденная ошибка, плюс общие помощники для всех проверок.
Все проверки отдают ошибки в одном формате, чтобы бэкенду и фронту было проще.
"""

# Каждый тип ошибки входит в одну из 4 групп, по ним фронт и группирует
CATEGORIES = {
    "missing": "missing",                 # пропуски
    "duplicate_row": "duplicate",         # дубликаты
    "duplicate_key": "duplicate",
    "wrong_type": "invalid",              # некорректные значения
    "out_of_range": "invalid",
    "wrong_format": "invalid",
    "wrong_date": "invalid",
    "not_allowed": "invalid",
    "inconsistent": "inconsistency",      # несогласованности
}


def get_category(issue_type):
    """Группа по типу ошибки."""
    return CATEGORIES.get(issue_type, "invalid")


def get_severity(percent):
    """Насколько всё плохо - по проценту строк с ошибкой."""
    if percent >= 20:
        return "high"
    if percent >= 5:
        return "medium"
    return "low"


def make_issue(issue_type, column, bad_rows, total_rows, message):
    """
    Собирает описание одной ошибки.

    issue_type - тип, например "missing" или "duplicate_row"
    column     - колонка (None, если речь про всю строку)
    bad_rows   - номера строк с ошибкой
    total_rows - сколько всего строк
    message    - текст для человека
    """
    count = len(bad_rows)

    if total_rows > 0:
        percent = round(count / total_rows * 100, 2)
    else:
        percent = 0

    return {
        "type": issue_type,
        "category": get_category(issue_type),
        "column": column,
        "count": count,
        "percent": percent,
        "severity": get_severity(percent),
        "message": message,
        "sample_rows": bad_rows[:5],  # хватит 5 примеров
    }


def to_number(series):
    """
    Колонка -> числа. Что не число (например "abc"), станет NaN.
    Запятую и пробелы тоже понимает: "1 234,5" -> 1234.5
    """
    import pandas as pd

    text = series.astype("string").str.strip()
    text = text.str.replace(" ", "", regex=False).str.replace("\u00a0", "", regex=False)
    text = text.str.replace(",", ".", regex=False)
    return pd.to_numeric(text, errors="coerce")


def to_dates(series, date_format=None):
    """
    Колонка -> даты. Неправильная дата станет NaT.
    В CSV даты приходят текстом ("01.02.2024"), а из Excel уже готовыми - понимаем оба случая.
    """
    import datetime

    import pandas as pd

    # Где уже лежит готовая дата (так бывает в Excel)
    is_date = series.map(lambda v: isinstance(v, (datetime.date, pd.Timestamp)))

    # Текст разбираем всей колонкой разом - так быстрее
    text = series.where(~is_date).astype("string").str.strip()
    if date_format:
        result = pd.to_datetime(text, format=date_format, errors="coerce")
    else:
        result = pd.to_datetime(text, errors="coerce", dayfirst=True)

    # Готовые даты просто подставляем
    if is_date.any():
        result[is_date] = pd.to_datetime(series[is_date].astype("object"))

    return result


def has_value(series):
    """True, если в ячейке что-то есть. Пусто - это None, NaN, "" и одни пробелы."""
    not_nan = series.notna()
    not_blank = series.astype(str).str.strip() != ""
    return not_nan & not_blank
