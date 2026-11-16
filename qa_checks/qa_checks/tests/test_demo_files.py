"""
Демо-файлы для защиты: в "грязных" должны найтись все 4 группы ошибок, в чистом - ничего.
Если упал - значит, после правок в проверках демо сломалось.
"""

import os

import pytest

from checks import check_file

TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_data")


@pytest.mark.parametrize("name", ["demo_orders.xlsx", "demo_employees.json", "demo_transactions_1c.csv"])
def test_dirty_demo_file_has_all_4_categories(name):
    summary = check_file(os.path.join(TEST_DATA, name))["summary"]
    assert all(summary[c] > 0 for c in ("missing", "duplicate", "invalid", "inconsistency")), summary


def test_clean_demo_file_has_no_errors():
    result = check_file(os.path.join(TEST_DATA, "demo_clean.csv"))
    assert result["issues"] == []
