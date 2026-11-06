"""
Ручной запуск: проверяет файл (CSV или Excel) по частям и печатает результат.

Запуск:                 python run.py
Свой файл:              python run.py путь/к/файлу.csv
Свой размер чанка:      python run.py путь/к/файлу.xlsx 50000
"""

import json
import sys
import time

from checks import check_file

file_path = sys.argv[1] if len(sys.argv) > 1 else "test_data/clients.csv"
chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100_000

# Настройки проверок (подходят для clients.csv и big.csv/big.xlsx)
config = {
    "key_columns": ["id"],
    "invalid_rules": {
        "age": {"type": "number", "min": 0, "max": 120},
        "email": {"type": "email"},
        "start_date": {"type": "date", "format": "%d.%m.%Y"},
        "end_date": {"type": "date", "format": "%d.%m.%Y"},
        "gender": {"allowed": ["М", "Ж"]},
    },
    "consistency_rules": [
        {"rule": "dates_order", "start": "start_date", "end": "end_date", "format": "%d.%m.%Y"},
        {"rule": "total", "price": "price", "quantity": "quantity", "total": "total"},
    ],
}


def show_progress(rows_done):
    print(f"  проверено строк: {rows_done:,}".replace(",", " "), end="\r")


started = time.time()
result = check_file(file_path, config, chunk_size=chunk_size, on_progress=show_progress)
seconds = round(time.time() - started, 1)

print(f"\nФайл: {file_path}")
print(f"Строк: {result['total_rows']}, колонок: {len(result['columns'])}, время: {seconds} сек")
print(f"Найдено проблем: {len(result['issues'])}\n")

for issue in result["issues"]:
    print(f"[{issue['severity']:6}] {issue['message']}  "
          f"(всего: {issue['count']}, примеры строк: {issue['sample_rows']})")

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print("\nПолный результат сохранён в result.json")
