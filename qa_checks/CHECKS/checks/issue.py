"""формат ошибки и общие помощники"""

# тип -> группа
CATEGORIES = {
    "missing": "missing",                 # пропуски
    "duplicate_row": "duplicate",         # дубликаты
    "duplicate_key": "duplicate",
    "wrong_type": "invalid",              # некорректные
    "out_of_range": "invalid",
    "wrong_format": "invalid",
    "wrong_date": "invalid",
    "not_allowed": "invalid",
    "inconsistent": "inconsistency",      # несогласованности
}


def get_category(issue_type):
    """группа по типу"""
    return CATEGORIES.get(issue_type, "invalid")


def get_severity(percent):
    """серьёзность по проценту"""
    if percent >= 20:
        return "high"
    if percent >= 5:
        return "medium"
    return "low"


def make_issue(issue_type, column, bad_rows, total_rows, message):
    """описание одной ошибки"""
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
        "sample_rows": bad_rows[:5],  # 5 примеров
    }


def to_number(series):
    """колонка -> числа, не число -> NaN"""
    import pandas as pd

    text = series.astype("string").str.strip()
    text = text.str.replace(" ", "", regex=False).str.replace("\u00a0", "", regex=False)
    text = text.str.replace(",", ".", regex=False)
    return pd.to_numeric(text, errors="coerce")


def to_dates(series, date_format=None):
    """колонка -> даты, ошибка -> NaT"""
    import datetime

    import pandas as pd

    # готовые даты из Excel
    is_date = series.map(lambda v: isinstance(v, (datetime.date, pd.Timestamp)))

    # парсим колонкой разом
    text = series.where(~is_date).astype("string").str.strip()
    if date_format:
        result = pd.to_datetime(text, format=date_format, errors="coerce")
    else:
        result = pd.to_datetime(text, errors="coerce", dayfirst=True)

    # подставляем готовые
    if is_date.any():
        result[is_date] = pd.to_datetime(series[is_date].astype("object"))

    return result


def has_value(series):
    """есть ли значение в ячейке"""
    not_nan = series.notna()
    not_blank = series.astype(str).str.strip() != ""
    return not_nan & not_blank
