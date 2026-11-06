"""
Тесты чтения JSON.

Главная проверка: clients.json содержит те же данные и ошибки, что clients.csv,
значит и найденные проблемы должны совпасть (плюс пустой город в address.city).
"""

import json
import os

from checks import check_file

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENTS_CSV = os.path.join(HERE, "..", "test_data", "clients.csv")
CLIENTS_JSON = os.path.join(HERE, "..", "test_data", "clients.json")

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
    return sorted((i["type"], str(i["column"]), i["count"], tuple(i["sample_rows"])) for i in issues)


def test_json_finds_same_errors_as_csv():
    csv_issues = check_file(CLIENTS_CSV, CONFIG)["issues"]
    json_result = check_file(CLIENTS_JSON, CONFIG, chunk_size=3)

    # В JSON есть ещё вложенное поле address.city, где один город пустой
    json_issues = [i for i in json_result["issues"] if i["column"] != "address.city"]
    assert short(json_issues) == short(csv_issues)
    assert "address.city" in json_result["columns"]


def test_nested_field_becomes_column():
    result = check_file(CLIENTS_JSON, CONFIG)
    city = [i for i in result["issues"] if i["column"] == "address.city"][0]

    assert city["type"] == "missing"
    assert city["sample_rows"] == [3]


def test_json_lines(tmp_path):
    path = tmp_path / "data.jsonl"
    lines = [{"id": 1, "email": "a@mail.ru"}, {"id": 2, "email": ""}, {"id": 1, "email": "c@mail.ru"}]
    path.write_text("\n".join(json.dumps(x) for x in lines), encoding="utf-8")

    result = check_file(str(path), {"key_columns": ["id"]}, chunk_size=2)
    types = {(i["type"], i["sample_rows"][0]) for i in result["issues"]}

    assert result["total_rows"] == 3
    assert ("missing", 1) in types
    assert ("duplicate_key", 2) in types


def test_wrapper_object(tmp_path):
    # Список лежит внутри {"meta": ..., "data": [...]}
    path = tmp_path / "wrapped.json"
    data = {"meta": {"source": "crm"}, "data": [{"id": 1}, {"id": 2}, {"id": None}]}
    path.write_text(json.dumps(data), encoding="utf-8")

    result = check_file(str(path))
    assert result["total_rows"] == 3
    assert result["issues"][0]["sample_rows"] == [2]


def test_field_appears_later(tmp_path):
    # Поле "phone" есть только у последней записи -> у первых 4 оно пустое
    path = tmp_path / "late.json"
    data = [{"id": i} for i in range(4)] + [{"id": 4, "phone": "123"}]
    path.write_text(json.dumps(data), encoding="utf-8")

    result = check_file(str(path), chunk_size=2)  # phone появится только в 3-й части
    phone = [i for i in result["issues"] if i["column"] == "phone"][0]

    assert phone["count"] == 4
    assert phone["percent"] == 80.0
    assert phone["sample_rows"] == [0, 1, 2, 3]


def test_numbers_stay_integers(tmp_path):
    # id 7 не должен превращаться в 7.0, даже если где-то id пустой
    path = tmp_path / "ids.json"
    path.write_text(json.dumps([{"id": 7}, {"id": None}, {"id": 7}]), encoding="utf-8")

    result = check_file(str(path), {"key_columns": ["id"]})
    dup = [i for i in result["issues"] if i["type"] == "duplicate_key"][0]
    assert dup["sample_rows"] == [2]
