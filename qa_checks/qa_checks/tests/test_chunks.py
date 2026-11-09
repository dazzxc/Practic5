"""
Тесты чтения по частям.

Главная идея: результат должен быть ОДИНАКОВЫМ,
читаем ли мы файл целиком или маленькими кусочками по 3 строки.
"""

import datetime
import os

import pandas as pd
from openpyxl import Workbook

from checks import check_file, run_all_checks

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENTS = os.path.join(HERE, "..", "test_data", "clients.csv")

CONFIG = {
    "key_columns": ["id"],
    "invalid_rules": {
        "age": {"type": "number", "min": 0, "max": 120},
        "email": {"type": "email"},
        "start_date": {"type": "date", "format": "%d.%m.%Y"},
        "gender": {"allowed": ["М", "Ж"]},
    },
    "consistency_rules": [
        {"rule": "dates_order", "start": "start_date", "end": "end_date", "format": "%d.%m.%Y"},
        {"rule": "total", "price": "price", "quantity": "quantity", "total": "total"},
    ],
}


def short(issues):
    """Оставляем главное, чтобы удобно сравнивать."""
    return sorted((i["type"], str(i["column"]), i["count"], tuple(i["sample_rows"])) for i in issues)


def test_chunks_give_same_result_as_whole_file():
    whole = run_all_checks(pd.read_csv(CLIENTS, dtype=str), CONFIG)
    by_chunks = check_file(CLIENTS, CONFIG, chunk_size=3)["issues"]

    assert short(by_chunks) == short(whole)


def test_duplicate_in_different_chunks_is_found():
    # Строка 1 и её копия (строка 8) попадают в РАЗНЫЕ чанки по 3 строки
    result = check_file(CLIENTS, CONFIG, chunk_size=3)
    dup = [i for i in result["issues"] if i["type"] == "duplicate_row"][0]

    assert dup["sample_rows"] == [8]


def test_row_numbers_are_global():
    # Пустое имя в строке 9 (последний чанк) - номер должен быть 9, а не 0
    result = check_file(CLIENTS, CONFIG, chunk_size=3)
    missing_name = [i for i in result["issues"]
                    if i["type"] == "missing" and i["column"] == "name"][0]

    assert missing_name["sample_rows"] == [9]
    assert result["total_rows"] == 10


def test_count_is_full_even_if_more_than_5_errors(tmp_path):
    # 20 пустых email - count должен быть 20, а примеров только 5
    path = tmp_path / "many.csv"
    pd.DataFrame({"email": [""] * 20, "x": range(20)}).to_csv(path, index=False)

    result = check_file(str(path), chunk_size=7)
    issue = result["issues"][0]
    assert issue["count"] == 20
    assert issue["percent"] == 100.0
    assert len(issue["sample_rows"]) == 5


def test_excel_file(tmp_path):
    path = tmp_path / "data.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["id", "age", "start_date", "end_date"])
    ws.append([1, 25, datetime.date(2024, 1, 1), datetime.date(2024, 1, 10)])
    ws.append([2, -5, datetime.date(2024, 5, 10), datetime.date(2024, 5, 1)])  # возраст и даты
    ws.append([1, None, "32.13.2024", datetime.date(2024, 1, 1)])              # дубль id, пусто, плохая дата
    wb.save(path)

    config = {
        "key_columns": ["id"],
        "invalid_rules": {"age": {"type": "number", "min": 0, "max": 120},
                          "start_date": {"type": "date", "format": "%d.%m.%Y"}},
        "consistency_rules": [{"rule": "dates_order", "start": "start_date",
                               "end": "end_date", "format": "%d.%m.%Y"}],
    }
    result = check_file(str(path), config, chunk_size=2)
    types = {(i["type"], i["sample_rows"][0]) for i in result["issues"]}

    assert ("missing", 2) in types
    assert ("duplicate_key", 2) in types
    assert ("out_of_range", 1) in types
    assert ("wrong_date", 2) in types
    assert ("inconsistent", 1) in types
    assert result["total_rows"] == 3


def test_semicolon_and_cp1251(tmp_path):
    # Excel в России часто сохраняет CSV через ";" и в кодировке Windows-1251
    path = tmp_path / "ru.csv"
    path.write_bytes("name;age\nАня;25\n;30\n".encode("cp1251"))

    result = check_file(str(path))
    assert result["columns"] == ["name", "age"]
    assert result["issues"][0]["column"] == "name"
