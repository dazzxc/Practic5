"""проверка 3: некорректные значения"""

import pandas as pd

from checks.issue import make_issue, has_value, to_dates, to_number

# x@y.z
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def check_number(df, column, rule):
    """число в пределах min/max"""
    issues = []
    total = len(df)
    filled = has_value(df[column])

    numbers = to_number(df[column])

    # не число
    not_number = filled & numbers.isna()
    bad_rows = df.index[not_number].tolist()
    if bad_rows:
        issues.append(make_issue("wrong_type", column, bad_rows, total,
                                 f"В колонке '{column}' есть значения, которые не являются числом"))

    # вне диапазона
    out_of_range = pd.Series(False, index=df.index)
    if "min" in rule:
        out_of_range |= numbers < rule["min"]
    if "max" in rule:
        out_of_range |= numbers > rule["max"]

    bad_rows = df.index[out_of_range].tolist()
    if bad_rows:
        issues.append(make_issue("out_of_range", column, bad_rows, total,
                                 f"В колонке '{column}' значения вне диапазона "
                                 f"{rule.get('min', '-∞')}..{rule.get('max', '+∞')}"))
    return issues


def check_email(df, column):
    """похоже на email"""
    filled = has_value(df[column])
    is_ok = df[column].astype(str).str.strip().str.match(EMAIL_PATTERN)
    bad_rows = df.index[filled & ~is_ok].tolist()

    if not bad_rows:
        return []
    return [make_issue("wrong_format", column, bad_rows, len(df),
                       f"В колонке '{column}' неправильный формат email")]


def check_date(df, column, date_format=None):
    """дата существует"""
    filled = has_value(df[column])
    dates = to_dates(df[column], date_format)
    bad_rows = df.index[filled & dates.isna()].tolist()

    if not bad_rows:
        return []
    return [make_issue("wrong_date", column, bad_rows, len(df),
                       f"В колонке '{column}' есть несуществующие или неправильные даты")]


def check_allowed(df, column, allowed):
    """значение из списка"""
    filled = has_value(df[column])
    allowed_str = [str(a) for a in allowed]
    is_ok = df[column].astype(str).str.strip().isin(allowed_str)
    bad_rows = df.index[filled & ~is_ok].tolist()

    if not bad_rows:
        return []
    # обрезаем длинный список
    shown = ", ".join(allowed_str[:5]) + (", ..." if len(allowed_str) > 5 else "")
    return [make_issue("not_allowed", column, bad_rows, len(df),
                       f"В колонке '{column}' есть недопустимые значения (разрешены: {shown})")]


def check_invalid(df, rules):
    """проверки по rules"""
    issues = []

    for column, rule in rules.items():
        if column not in df.columns:
            continue

        kind = rule.get("type")
        if kind == "number":
            issues += check_number(df, column, rule)
        elif kind == "email":
            issues += check_email(df, column)
        elif kind == "date":
            issues += check_date(df, column, rule.get("format"))

        if "allowed" in rule:
            issues += check_allowed(df, column, rule["allowed"])

    return issues
