"""
Ручной запуск: проверяет файл (CSV, Excel или JSON) по частям и печатает результат.
Правила подбираются автоматически (см. checks/auto_rules.py).

Запуск:                 python run.py
Свой файл:              python run.py путь/к/файлу.csv
Свой размер чанка:      python run.py путь/к/файлу.xlsx 50000
Свои правила вручную:   python run.py путь/к/файлу.csv 15000 manual
"""

import json
import sys
import time

from checks import check_file
from checks.reader import DEFAULT_CHUNK_SIZE

file_path = sys.argv[1] if len(sys.argv) > 1 else "test_data/clients.csv"
chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CHUNK_SIZE

use_manual = len(sys.argv) > 3 and sys.argv[3] == "manual"

# Пример правил, заданных вручную (подходят для clients.csv и big.csv).
# Используются только с флагом manual, иначе правила подбираются сами.
MANUAL_CONFIG = {
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
config = MANUAL_CONFIG if use_manual else None  # None = подобрать правила автоматически
result = check_file(file_path, config, chunk_size=chunk_size, on_progress=show_progress)
seconds = round(time.time() - started, 1)

print(f"\nФайл: {file_path}")
print(f"Строк: {result['total_rows']}, колонок: {len(result['columns'])}, время: {seconds} сек")
print("Правила:", "заданы вручную" if use_manual else "подобраны автоматически")
print(json.dumps(result["config"], ensure_ascii=False, indent=2))
print(f"\nИтого по группам: {result['summary']}")
print(f"Найдено проблем: {len(result['issues'])}\n")

for issue in result["issues"]:
    print(f"[{issue['severity']:6}] {issue['message']}  "
          f"(всего: {issue['count']}, примеры строк: {issue['sample_rows']})")

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print("\nПолный результат сохранён в result.json")
