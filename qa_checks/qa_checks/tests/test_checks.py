"""
Тесты проверок. Запуск из папки qa_checks: pytest

Делаем маленькую таблицу, где заранее знаем все ошибки, и смотрим, что их нашли.
"""

import pandas as pd

from checks.missing import check_missing
from checks.duplicates import check_duplicates
from checks.invalid import check_invalid
from checks.consistency import check_consistency


# ---------- 1. Пропуски ----------

def test_missing_finds_none_nan_and_empty_string():
    df = pd.DataFrame({
        "name": ["Аня", None, "Петя", "   "],  # 2 пропуска: None и пробелы
        "age": [20, 30, float("nan"), 40],    # 1 пропуск: NaN
        "city": ["Москва", "Казань", "Сочи", "Омск"],  # без пропусков
    })
    issues = check_missing(df)

    by_column = {i["column"]: i for i in issues}
    assert set(by_column) == {"name", "age"}      # city не должно быть
    assert by_column["name"]["count"] == 2
    assert by_column["name"]["sample_rows"] == [1, 3]
    assert by_column["age"]["count"] == 1
    assert by_column["name"]["percent"] == 50.0


def test_missing_nothing_found():
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert check_missing(df) == []


# ---------- 2. Дубликаты ----------

def test_full_duplicates():
    df = pd.DataFrame({"id": [1, 2, 1], "name": ["Аня", "Петя", "Аня"]})
    issues = check_duplicates(df)

    assert len(issues) == 1
    assert issues[0]["type"] == "duplicate_row"
    assert issues[0]["sample_rows"] == [2]  # копия - третья строка


def test_key_duplicates():
    df = pd.DataFrame({"id": [1, 2, 1], "name": ["Аня", "Петя", "Дима"]})
    issues = check_duplicates(df, key_columns=["id"])

    types = [i["type"] for i in issues]
    assert "duplicate_row" not in types  # строки разные (имена другие)
    assert "duplicate_key" in types


# ---------- 3. Некорректные значения ----------

def test_number_type_and_range():
    df = pd.DataFrame({"age": ["25", "abc", "-5", "300", None]})
    issues = check_invalid(df, {"age": {"type": "number", "min": 0, "max": 120}})

    by_type = {i["type"]: i for i in issues}
    assert by_type["wrong_type"]["sample_rows"] == [1]       # "abc"
    assert by_type["out_of_range"]["sample_rows"] == [2, 3]  # -5 и 300
    # None не считается ошибкой здесь (это работа missing.py)


def test_email_format():
    df = pd.DataFrame({"email": ["a@mail.ru", "bad-mail.ru", "x@y", ""]})
    issues = check_invalid(df, {"email": {"type": "email"}})

    assert issues[0]["sample_rows"] == [1, 2]


def test_wrong_date():
    df = pd.DataFrame({"d": ["01.01.2024", "32.13.2024"]})
    issues = check_invalid(df, {"d": {"type": "date", "format": "%d.%m.%Y"}})

    assert issues[0]["type"] == "wrong_date"
    assert issues[0]["sample_rows"] == [1]


def test_allowed_values():
    df = pd.DataFrame({"gender": ["М", "Ж", "X"]})
    issues = check_invalid(df, {"gender": {"allowed": ["М", "Ж"]}})

    assert issues[0]["sample_rows"] == [2]


# ---------- 4. Несогласованности ----------

def test_end_date_before_start_date():
    df = pd.DataFrame({
        "start": ["01.01.2024", "10.05.2024"],
        "end": ["05.01.2024", "01.05.2024"],  # во второй строке конец раньше начала
    })
    issues = check_consistency(df, [{"rule": "dates_order", "start": "start", "end": "end",
                                     "format": "%d.%m.%Y"}])

    assert issues[0]["sample_rows"] == [1]


def test_total_not_equal_price_times_quantity():
    df = pd.DataFrame({"price": [100, 20], "qty": [2, 4], "total": [200, 100]})  # 20*4=80, а не 100
    issues = check_consistency(df, [{"rule": "total", "price": "price",
                                     "quantity": "qty", "total": "total"}])

    assert issues[0]["sample_rows"] == [1]
