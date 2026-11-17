"""автоподбор правил по первому куску"""

import re

import pandas as pd

from checks.issue import has_value, to_number

# порог доли для числа/даты
MATCH_SHARE = 0.8

# форматы дат
DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
]

# ключевые слова колонок
EMAIL_WORDS = ["email", "e-mail", "mail", "почта"]
AGE_WORDS = ["age", "возраст"]
NOT_NEGATIVE_WORDS = ["price", "cost", "amount", "sum", "total", "qty", "quantity", "count",
                      "цена", "стоимость", "сумма", "итог", "количество", "кол-во"]
GENDER_WORDS = ["gender", "sex", "пол"]
GENDER_VALUES = ["М", "Ж", "M", "F", "м", "ж", "m", "f", "Муж", "Жен", "муж", "жен",
                 "Мужской", "Женский", "мужской", "женский", "male", "female", "Male", "Female"]

# поиск опечаток:
ENUM_MAX_VALUES = 10     # до 10 значений
ENUM_MIN_ROWS = 200      # от 200 строк
ENUM_RARE_SHARE = 0.005  # реже 0,5% - опечатка

PRICE_WORDS = ["price", "цена", "стоимость"]
QUANTITY_WORDS = ["quantity", "qty", "count", "количество", "кол-во"]
TOTAL_WORDS = ["total", "sum", "amount", "сумма", "итог"]
START_WORDS = ["start", "begin", "created", "from", "open", "order", "hire", "issue",
               "начал", "создан", "открыт", "заказ", "найм", "приём", "прием", "выдач"]
END_WORDS = ["end", "finish", "complet", "close", "until", "deliver", "expir", "due", "deadline",
             "оконч", "заверш", "закрыт", "доставк", "увольн", "срок"]


def _name(column):
    return str(column).strip().lower()


def _has_word(column, words):
    name = _name(column)
    return any(word in name for word in words)


def _is_id_name(column):
    """похоже на id"""
    name = _name(column)
    return name == "id" or name.endswith("id") or name.endswith("_id") or name in ("номер", "код")


def _filled(series):
    """непустые значения текстом"""
    return series[has_value(series)].astype(str).str.strip()


def _number_share(values):
    """доля чисел"""
    if len(values) == 0:
        return 0
    return to_number(values).notna().mean()


def _detect_date_format(values):
    """формат большинства или None"""
    if len(values) == 0:
        return None
    for date_format in DATE_FORMATS:
        parsed = pd.to_datetime(values, format=date_format, errors="coerce")
        if parsed.notna().mean() >= MATCH_SHARE:
            return date_format
    return None


def suggest_rules(sample):
    """config по первому куску"""
    invalid_rules = {}
    key_columns = []
    date_columns = {}     # колонка -> формат
    number_columns = []

    for column in sample.columns:
        values = _filled(sample[column])
        if len(values) == 0:
            continue  # пустая колонка

        # email
        email_share = values.str.contains("@", regex=False).mean()
        if _has_word(column, EMAIL_WORDS) or email_share > 0.5:
            invalid_rules[column] = {"type": "email"}
            continue

        # дата (до числа)
        date_format = _detect_date_format(values)
        if date_format:
            invalid_rules[column] = {"type": "date", "format": date_format}
            date_columns[column] = date_format
            continue

        # число
        if _number_share(values) >= MATCH_SHARE:
            rule = {"type": "number"}
            if _has_word(column, AGE_WORDS):
                rule.update({"min": 0, "max": 120})
            elif _has_word(column, NOT_NEGATIVE_WORDS):
                rule["min"] = 0
            invalid_rules[column] = rule
            number_columns.append(column)

        # ключ: id и почти без повторов
        if _is_id_name(column) and values.nunique() >= 0.8 * len(values):
            key_columns.append(column)

        if column in invalid_rules:
            continue  # правило уже есть

        # разрешённые значения
        allowed = _suggest_allowed(column, values)
        if allowed:
            invalid_rules[column] = {"allowed": allowed}

    consistency_rules = _find_date_pairs(date_columns) + _find_total_rule(number_columns)

    return {
        "key_columns": key_columns,
        "invalid_rules": invalid_rules,
        "consistency_rules": consistency_rules,
    }


def _suggest_allowed(column, values):
    """разрешённые значения или None"""
    if _name(column) in GENDER_WORDS or _has_word(column, ["gender"]):
        return GENDER_VALUES

    counts = values.value_counts()
    if len(values) < ENUM_MIN_ROWS or not (2 <= len(counts) <= ENUM_MAX_VALUES):
        return None
    frequent = counts[counts >= ENUM_RARE_SHARE * len(values)]
    return [str(v) for v in frequent.index]


def _strip_words(column, words):
    """start_date -> _date"""
    name = _name(column)
    for word in words:
        name = re.sub(word + r"\w*", "", name)
    return name


def _find_date_pairs(date_columns):
    """пары дат начало/конец"""
    starts = [c for c in date_columns if _has_word(c, START_WORDS)]
    ends = [c for c in date_columns if _has_word(c, END_WORDS)]
    pairs = []

    for start in starts:
        # пара с тем же остатком
        base = _strip_words(start, START_WORDS)
        match = [e for e in ends if _strip_words(e, END_WORDS) == base and e != start]
        # единственный конец
        if not match and len(ends) == 1 and ends[0] != start:
            match = ends
        if match:
            end = match[0]
            pairs.append({
                "rule": "dates_order",
                "start": start,
                "end": end,
                "start_format": date_columns[start],
                "end_format": date_columns[end],
            })
    return pairs


def _find_total_rule(number_columns):
    """цена × количество = итог"""
    def first(words):
        found = [c for c in number_columns if _has_word(c, words)]
        return found[0] if found else None

    price = first(PRICE_WORDS)
    quantity = first(QUANTITY_WORDS)
    total = first(TOTAL_WORDS)
    if price and quantity and total and len({price, quantity, total}) == 3:
        return [{"rule": "total", "price": price, "quantity": quantity, "total": total}]
    return []
