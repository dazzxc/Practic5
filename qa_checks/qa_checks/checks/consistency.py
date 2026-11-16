"""
Проверка 4: несогласованности между колонками.

Два простых правила:
1. Дата окончания не может быть раньше даты начала.
2. Сумма должна быть равна цене, умноженной на количество.
"""

import pandas as pd

from checks.issue import make_issue, to_dates, to_number


def check_dates_order(df, start_column, end_column, date_format=None, end_format=None):
    """
    Ищет строки, где дата окончания раньше даты начала.
    end_format - если у даты окончания другой формат (по умолчанию такой же, как у начала).
    """
    if start_column not in df.columns or end_column not in df.columns:
        return []

    start = to_dates(df[start_column], date_format)
    end = to_dates(df[end_column], end_format or date_format)

    # Сравниваем только там, где обе даты правильные
    wrong = start.notna() & end.notna() & (end < start)
    bad_rows = df.index[wrong].tolist()

    if not bad_rows:
        return []
    return [make_issue("inconsistent", f"{start_column} / {end_column}", bad_rows, len(df),
                       f"'{end_column}' раньше, чем '{start_column}'")]


def check_total(df, price_column, quantity_column, total_column):
    """Ищет строки, где сумма не равна цене, умноженной на количество."""
    for col in (price_column, quantity_column, total_column):
        if col not in df.columns:
            return []

    price = to_number(df[price_column])
    quantity = to_number(df[quantity_column])
    total = to_number(df[total_column])

    expected = price * quantity
    # Сравниваем с маленьким допуском (0.01), чтобы копейки при округлении не считались ошибкой
    wrong = expected.notna() & total.notna() & ((expected - total).abs() > 0.01)
    bad_rows = df.index[wrong].tolist()

    if not bad_rows:
        return []
    return [make_issue("inconsistent", total_column, bad_rows, len(df),
                       f"'{total_column}' не равна '{price_column}' × '{quantity_column}'")]


def check_consistency(df, rules):
    """
    Запускает правила из списка. Пример:

    rules = [
        {"rule": "dates_order", "start": "start_date", "end": "end_date"},
        {"rule": "total", "price": "price", "quantity": "quantity", "total": "total"},
    ]
    """
    issues = []
    for r in rules:
        if r["rule"] == "dates_order":
            start_format = r.get("start_format", r.get("format"))
            end_format = r.get("end_format", r.get("format"))
            issues += check_dates_order(df, r["start"], r["end"], start_format, end_format)
        elif r["rule"] == "total":
            issues += check_total(df, r["price"], r["quantity"], r["total"])
    return issues
