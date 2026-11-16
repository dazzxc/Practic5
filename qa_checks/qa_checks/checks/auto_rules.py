"""
Автоматический подбор правил проверки для ЛЮБОГО файла.

Зачем: пользователь загружает файл с любыми колонками (например
transaction_id, amount, created_at), а писать правила руками некогда.
Эта функция смотрит на первую часть файла и сама решает, что проверять.

Как она угадывает (простые правила):
1. Email   - в названии есть email/mail/почта ИЛИ больше половины значений содержат "@".
2. Число   - 80% и больше значений - числа. Тогда остальные (текст) - ошибка.
             Для возраста, цены, количества и сумм - ещё и "не меньше 0".
3. Дата    - 80% и больше значений подходят под один из популярных форматов дат.
4. Ключ    - название похоже на id и значения в основном разные -> ищем повторы.
5. Список  - пол (gender/пол) -> только М/Ж и их варианты. Для остальных текстовых
             колонок с 2-10 разными значениями (если строк от 200) - редкие значения
             (меньше 0,5%) считаются опечатками.
6. Пары дат - начало/конец (start/end, created/completed, ...) -> конец не раньше начала.
7. Сумма   - есть цена, количество и итог -> итог = цена × количество.

Результат - обычный config, такой же, как пишется вручную.
"""

import re

import pandas as pd

from checks.issue import has_value, to_number

# Сколько значений должно подойти, чтобы считать колонку числом/датой
MATCH_SHARE = 0.8

# Популярные форматы дат. Проверяем по очереди, берём первый подошедший.
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

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# Слова в названиях колонок (в нижнем регистре)
EMAIL_WORDS = ["email", "e-mail", "mail", "почта"]
AGE_WORDS = ["age", "возраст"]
NOT_NEGATIVE_WORDS = ["price", "cost", "amount", "sum", "total", "qty", "quantity", "count",
                      "цена", "стоимость", "сумма", "итог", "количество", "кол-во"]
GENDER_WORDS = ["gender", "sex", "пол"]
GENDER_VALUES = ["М", "Ж", "M", "F", "м", "ж", "m", "f", "Муж", "Жен", "муж", "жен",
                 "Мужской", "Женский", "мужской", "женский", "male", "female", "Male", "Female"]

# Поиск списка допустимых значений для обычных текстовых колонок
ENUM_MAX_VALUES = 10     # не больше 10 разных значений
ENUM_MIN_ROWS = 200      # и хотя бы 200 заполненных строк, иначе статистике верить нельзя
ENUM_RARE_SHARE = 0.005  # значение встречается реже 0,5% -> похоже на опечатку

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
    """id, ID, user_id, SteamID, transaction_id, номер..."""
    name = _name(column)
    return name == "id" or name.endswith("id") or name.endswith("_id") or name in ("номер", "код")


def _filled(series):
    """Только заполненные значения колонки, как текст без пробелов по краям."""
    return series[has_value(series)].astype(str).str.strip()


def _number_share(values):
    """Какая доля значений - числа."""
    if len(values) == 0:
        return 0
    return to_number(values).notna().mean()


def _detect_date_format(values):
    """Ищет формат даты, под который подходит большинство значений. Иначе None."""
    if len(values) == 0:
        return None
    for date_format in DATE_FORMATS:
        parsed = pd.to_datetime(values, format=date_format, errors="coerce")
        if parsed.notna().mean() >= MATCH_SHARE:
            return date_format
    return None


def suggest_rules(sample):
    """
    Получает первую часть файла (DataFrame) и возвращает config для check_file.
    """
    invalid_rules = {}
    key_columns = []
    date_columns = {}     # колонка -> формат
    number_columns = []

    for column in sample.columns:
        values = _filled(sample[column])
        if len(values) == 0:
            continue  # колонка пустая - тут только пропуски

        # 1) Email
        email_share = values.str.contains("@", regex=False).mean()
        if _has_word(column, EMAIL_WORDS) or email_share > 0.5:
            invalid_rules[column] = {"type": "email"}
            continue

        # 2) Дата (проверяем раньше числа, чтобы 20240105 не стало датой случайно - форматы строгие)
        date_format = _detect_date_format(values)
        if date_format:
            invalid_rules[column] = {"type": "date", "format": date_format}
            date_columns[column] = date_format
            continue

        # 3) Число
        if _number_share(values) >= MATCH_SHARE:
            rule = {"type": "number"}
            if _has_word(column, AGE_WORDS):
                rule.update({"min": 0, "max": 120})
            elif _has_word(column, NOT_NEGATIVE_WORDS):
                rule["min"] = 0
            invalid_rules[column] = rule
            number_columns.append(column)

        # 4) Ключ: название похоже на id и значения в основном разные
        #    (customer_id в таблице заказов повторяется часто - это не ключ)
        if _is_id_name(column) and values.nunique() >= 0.8 * len(values):
            key_columns.append(column)

        if column in invalid_rules:
            continue  # это число - список значений не нужен

        # 5) Список допустимых значений
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
    """Подбирает список допустимых значений для колонки (или None)."""
    if _name(column) in GENDER_WORDS or _has_word(column, ["gender"]):
        return GENDER_VALUES

    counts = values.value_counts()
    if len(values) < ENUM_MIN_ROWS or not (2 <= len(counts) <= ENUM_MAX_VALUES):
        return None
    frequent = counts[counts >= ENUM_RARE_SHARE * len(values)]
    return [str(v) for v in frequent.index]


def _strip_words(column, words):
    """Убирает из названия слова начала/конца, чтобы сравнить остаток: start_date -> _date."""
    name = _name(column)
    for word in words:
        name = re.sub(word + r"\w*", "", name)
    return name


def _find_date_pairs(date_columns):
    """Находит пары дат начало/конец."""
    starts = [c for c in date_columns if _has_word(c, START_WORDS)]
    ends = [c for c in date_columns if _has_word(c, END_WORDS)]
    pairs = []

    for start in starts:
        # Сначала ищем конец с таким же "остатком" названия (start_date / end_date)
        base = _strip_words(start, START_WORDS)
        match = [e for e in ends if _strip_words(e, END_WORDS) == base and e != start]
        # Если такого нет, но конец всего один - берём его (created_at / completed_at)
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
    """Если есть цена, количество и итог - проверяем итог = цена × количество."""
    def first(words):
        found = [c for c in number_columns if _has_word(c, words)]
        return found[0] if found else None

    price = first(PRICE_WORDS)
    quantity = first(QUANTITY_WORDS)
    total = first(TOTAL_WORDS)
    if price and quantity and total and len({price, quantity, total}) == 3:
        return [{"rule": "total", "price": price, "quantity": quantity, "total": total}]
    return []
