"""проверка 4: несогласованности"""

from checks.issue import make_issue, to_dates, to_number


def check_dates_order(df, start_column, end_column, date_format=None, end_format=None):
    """конец раньше начала"""
    if start_column not in df.columns or end_column not in df.columns:
        return []

    start = to_dates(df[start_column], date_format)
    end = to_dates(df[end_column], end_format or date_format)

    # только корректные даты
    wrong = start.notna() & end.notna() & (end < start)
    bad_rows = df.index[wrong].tolist()

    if not bad_rows:
        return []
    return [make_issue("inconsistent", f"{start_column} / {end_column}", bad_rows, len(df),
                       f"'{end_column}' раньше, чем '{start_column}'")]


def check_total(df, price_column, quantity_column, total_column):
    """итог != цена × количество"""
    for col in (price_column, quantity_column, total_column):
        if col not in df.columns:
            return []

    price = to_number(df[price_column])
    quantity = to_number(df[quantity_column])
    total = to_number(df[total_column])

    expected = price * quantity
    # допуск на округление
    wrong = expected.notna() & total.notna() & ((expected - total).abs() > 0.01)
    bad_rows = df.index[wrong].tolist()

    if not bad_rows:
        return []
    return [make_issue("inconsistent", total_column, bad_rows, len(df),
                       f"'{total_column}' не равна '{price_column}' × '{quantity_column}'")]


def check_consistency(df, rules):
    """запуск правил из списка"""
    issues = []
    for r in rules:
        if r["rule"] == "dates_order":
            start_format = r.get("start_format", r.get("format"))
            end_format = r.get("end_format", r.get("format"))
            issues += check_dates_order(df, r["start"], r["end"], start_format, end_format)
        elif r["rule"] == "total":
            issues += check_total(df, r["price"], r["quantity"], r["total"])
    return issues
