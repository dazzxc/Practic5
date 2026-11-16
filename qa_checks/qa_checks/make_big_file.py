"""
Делает большой тестовый файл, чтобы проверить чтение кусками.

Запуск:
    python make_big_file.py 1000000          -> test_data/big.csv на 1 млн строк
    python make_big_file.py 200000 xlsx      -> test_data/big.xlsx на 200 тыс. строк
    python make_big_file.py 500000 json      -> test_data/big.json на 500 тыс. записей

Ошибки добавлены специально, примерно по 1% строк каждого вида.
"""

import random
import sys

rows = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
file_type = sys.argv[2] if len(sys.argv) > 2 else "csv"

random.seed(42)
HEADER = ["id", "name", "email", "age", "gender", "start_date",
          "end_date", "price", "quantity", "total"]


def make_row(i):
    price, qty = random.randint(1, 500), random.randint(1, 10)
    row = [i, f"Клиент {i}", f"user{i}@mail.ru", random.randint(18, 80),
           random.choice(["М", "Ж"]), "01.03.2024", "15.03.2024", price, qty, price * qty]

    r = random.random()
    if r < 0.01:
        row[2] = ""                 # пустой email
    elif r < 0.02:
        row[2] = "bad-email"        # неправильный email
    elif r < 0.03:
        row[3] = -1                 # плохой возраст
    elif r < 0.04:
        row[4] = "X"                # недопустимый пол
    elif r < 0.05:
        row[6] = "01.01.2024"       # конец раньше начала
    elif r < 0.06:
        row[9] = row[9] + 1         # сумма не сходится
    elif r < 0.07 and i > 0:
        row[0] = i - 1              # дубль id
    return row


if file_type == "xlsx":
    from openpyxl import Workbook

    path = "test_data/big.xlsx"
    wb = Workbook(write_only=True)  # write_only, чтобы не держать всё в памяти
    ws = wb.create_sheet()
    ws.append(HEADER)
    for i in range(rows):
        ws.append(make_row(i))
    wb.save(path)
elif file_type == "json":
    import json

    path = "test_data/big.json"
    # Пишем по одной записи, чтобы не держать всё в памяти
    with open(path, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i in range(rows):
            record = dict(zip(HEADER, make_row(i)))
            f.write(("," if i else "") + json.dumps(record, ensure_ascii=False) + "\n")
        f.write("]\n")
else:
    import csv

    path = "test_data/big.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for i in range(rows):
            writer.writerow(make_row(i))

print(f"Готово: {path}, строк: {rows}")
