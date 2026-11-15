"""
Общий формат описания проблемы (Issue).

Все проверки возвращают проблемы в одном и том же виде,
чтобы Человек 5 (отчёты) и Человек 7 (дашборд) могли их легко прочитать.
"""

# Каждый тип проблемы относится к одной из 4 больших групп.
# Фронтенд группирует ошибки именно по этим группам.
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
    """По типу проблемы возвращает её группу."""
    return CATEGORIES.get(issue_type, "invalid")


def get_severity(percent):
    """Определяет, насколько серьёзна проблема, по проценту плохих строк."""
    if percent >= 20:
        return "high"  # серьёзно
    if percent >= 5:
        return "medium"  # средне
    return "low"  # не очень серьёзно


def make_issue(issue_type, column, bad_rows, total_rows, message):
    """
    Создаёт описание одной проблемы.

    issue_type - тип проблемы, например "missing" или "duplicate_row"
    column     - в какой колонке проблема (None, если касается всей строки)
    bad_rows   - список номеров строк с ошибкой
    total_rows - сколько всего строк в таблице
    message    - понятное человеку описание
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
        "sample_rows": bad_rows[:5],  # первые 5 примеров, больше не нужно
    }


def to_number(series):
    """
    Превращает колонку в числа. Если не получилось (например "abc"), будет NaN.
    Понимает запятую как дробную часть и пробелы между разрядами: "1 234,5" -> 1234.5
    """
    import pandas as pd

    text = series.astype("string").str.strip()
    text = text.str.replace(" ", "", regex=False).str.replace("\u00a0", "", regex=False)
    text = text.str.replace(",", ".", regex=False)
    return pd.to_numeric(text, errors="coerce")


def to_dates(series, date_format=None):
    """
    Превращает колонку в даты. Если дата неправильная - будет NaT (пусто).

    В CSV даты - это текст ("01.02.2024"), а в Excel - уже готовые даты.
    Эта функция понимает оба варианта.
    """
    import datetime

    import pandas as pd

    # 1) Находим ячейки, где уже лежит готовая дата (так бывает в Excel)
    is_date = series.map(lambda v: isinstance(v, (datetime.date, pd.Timestamp)))

    # 2) Текст разбираем сразу всей колонкой - это быстро
    text = series.where(~is_date).astype("string").str.strip()
    if date_format:
        result = pd.to_datetime(text, format=date_format, errors="coerce")
    else:
        result = pd.to_datetime(text, errors="coerce", dayfirst=True)

    # 3) Готовые даты подставляем как есть
    if is_date.any():
        result[is_date] = pd.to_datetime(series[is_date].astype("object"))

    return result


def has_value(series):
    """
    Возвращает True для ячеек, где что-то есть,
    и False для пустых (None, NaN, пустая строка, одни пробелы).
    """
    not_nan = series.notna()
    not_blank = series.astype(str).str.strip() != ""
    return not_nan & not_blank
