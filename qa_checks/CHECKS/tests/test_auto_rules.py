"""автоправила"""

import os

import pandas as pd

from checks import check_file, run_all_checks
from checks.auto_rules import suggest_rules

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENTS = os.path.join(HERE, "..", "test_data", "clients.csv")


def test_clients_without_config_finds_all_4_categories():
    result = check_file(CLIENTS)  # без config

    assert result["auto_rules"] is True
    summary = result["summary"]
    assert summary["missing"] > 0
    assert summary["duplicate"] > 0
    assert summary["invalid"] > 0
    assert summary["inconsistency"] > 0


def test_every_issue_has_category():
    result = check_file(CLIENTS)
    for issue in result["issues"]:
        assert issue["category"] in ("missing", "duplicate", "invalid", "inconsistency")


def test_transactions_like_file(tmp_path):
    # как реальный файл
    path = tmp_path / "transactions.csv"
    path.write_text(
        "transaction_id;customer_id;amount;created_at;completed_at\n"
        "1;100;50.5;2026-07-05 20:14:00;2026-07-10 20:14:00\n"
        "2;100;-10;2026-07-06 10:00:00;2026-07-07 10:00:00\n"      # отрицательная сумма
        "3;100;abc;2026-07-07 10:00:00;2026-07-01 10:00:00\n"      # не число + конец раньше
        "3;101;20;2026-07-08 10:00:00;2026-07-09 10:00:00\n"       # повтор id
        "5;101;30;2026-13-45 10:00:00;2026-07-09 10:00:00\n",      # несуществующая дата
        encoding="utf-8",
    )
    result = check_file(str(path))
    types = {i["type"] for i in result["issues"]}

    assert "transaction_id" in result["config"]["key_columns"]
    assert "customer_id" not in result["config"]["key_columns"]  # повтор клиента - норма
    assert {"out_of_range", "wrong_type", "wrong_date", "inconsistent", "duplicate_key"} <= types


def test_comma_decimal_is_a_number():
    df = pd.DataFrame({"price": ["10,5", "20,25", "1 000,5"] * 10})
    rules = suggest_rules(df)
    assert rules["invalid_rules"]["price"]["type"] == "number"

    issues = run_all_checks(df)
    assert [i for i in issues if i["type"] == "wrong_type"] == []


def test_text_column_is_not_checked_as_number():
    df = pd.DataFrame({"name": ["Аня", "Петя", "Иван"] * 10, "city": ["Москва"] * 30})
    rules = suggest_rules(df)
    assert "name" not in rules["invalid_rules"]


def test_rare_value_in_list_is_error():
    # опечатка BYU
    values = ["BUY", "SELL"] * 150
    values[10] = "BYU"
    df = pd.DataFrame({"intent": values})

    issues = [i for i in run_all_checks(df) if i["type"] == "not_allowed"]
    assert issues and issues[0]["sample_rows"] == [10]


def test_given_config_is_used_as_is():
    # ручные правила без автоподбора
    result = check_file(CLIENTS, {"key_columns": ["id"]})
    assert result["auto_rules"] is False
    assert result["summary"]["invalid"] == 0
