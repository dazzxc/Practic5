"""
Создаёт набор небольших демо-файлов для показа на защите.

Запуск (из папки qa_checks/qa_checks):
    python make_demo_files.py

Файлы появятся в test_data/:
    demo_orders.xlsx           - заказы магазина (Excel)
    demo_employees.json        - сотрудники (JSON со вложенным адресом)
    demo_transactions_1c.csv   - выгрузка как из 1С (разделитель ";", кодировка Windows-1251,
                                 русские названия колонок, дробные числа через запятую)
    demo_clean.csv             - чистый файл без ошибок

Во всех файлах, кроме demo_clean.csv, специально заложены ошибки всех 4 видов:
пропуски, дубликаты, некорректные значения и несогласованности.
"""

import csv
import datetime as dt
import json
import random

from openpyxl import Workbook

random.seed(2026)  # одинаковый результат при каждом запуске

FIRST_NAMES = ["Анна", "Иван", "Мария", "Пётр", "Ольга", "Дмитрий", "Елена", "Сергей",
               "Наталья", "Алексей", "Татьяна", "Михаил", "Юлия", "Андрей", "Светлана"]
LAST_NAMES = ["Иванов", "Петров", "Смирнов", "Кузнецов", "Попов", "Соколов", "Лебедев",
              "Козлов", "Новиков", "Морозов", "Волков", "Фёдоров"]
CITIES = ["Москва", "Санкт-Петербург", "Калининград", "Казань", "Новосибирск", "Екатеринбург"]
PRODUCTS = [("Ноутбук", 65000), ("Мышь", 1200), ("Клавиатура", 3500), ("Монитор", 18000),
            ("Наушники", 4500), ("Флешка 64 ГБ", 900), ("Веб-камера", 3900), ("Коврик", 600)]

START = dt.date(2025, 1, 1)


def random_date(days=300):
    return START + dt.timedelta(days=random.randint(0, days))


def latin_login(i):
    return f"user{i}"


def pick_rows(total, count, exclude=()):
    """Случайные номера строк для ошибок (не повторяются и не попадают в exclude)."""
    candidates = [i for i in range(total) if i not in exclude]
    return set(random.sample(candidates, count))


# ---------------------------------------------------------------------------
# 1. Заказы магазина (Excel)
# ---------------------------------------------------------------------------

def make_orders(path, rows=500):
    statuses = ["Новый", "Оплачен", "Отправлен", "Доставлен"]
    data = []
    for i in range(rows):
        product, price = random.choice(PRODUCTS)
        quantity = random.randint(1, 5)
        order_date = random_date()
        delivery = order_date + dt.timedelta(days=random.randint(1, 10))
        data.append({
            "order_id": 10000 + i,
            "customer_email": f"{latin_login(i)}@mail.ru",
            "product": product,
            "price": price,
            "quantity": quantity,
            "total": price * quantity,
            "order_date": order_date,
            "delivery_date": delivery,
            "status": random.choice(statuses),
        })

    used = set()
    def take(n):
        chosen = pick_rows(rows, n, used)
        used.update(chosen)
        return chosen

    for i in take(15):
        data[i]["customer_email"] = None                     # пропуск
    for i in take(6):
        data[i]["customer_email"] = f"{latin_login(i)}-mail.ru"  # неверный email
    for i in take(5):
        data[i]["price"] = -data[i]["price"]                 # отрицательная цена
        data[i]["total"] = data[i]["price"] * data[i]["quantity"]
    for i in take(4):
        data[i]["quantity"] = "два"                          # текст вместо числа
        data[i]["total"] = data[i]["price"] * 2
    for i in take(6):
        data[i]["total"] += 100                              # сумма не сходится
    for i in take(5):
        data[i]["delivery_date"] = data[i]["order_date"] - dt.timedelta(days=3)  # доставка раньше заказа
    for i in take(3):
        data[i]["order_date"] = "31.02.2025"                 # несуществующая дата
    for i in take(2):
        data[i]["status"] = "Доставлне"                      # опечатка в статусе
    for i in take(4):
        data[i]["order_id"] = data[i - 1]["order_id"]        # повтор номера заказа

    data += [dict(data[7]), dict(data[42])]                   # 2 полностью одинаковые строки

    wb = Workbook()
    ws = wb.active
    ws.title = "Заказы"
    ws.append(list(data[0].keys()))
    for row in data:
        ws.append(list(row.values()))
    for col in ("G", "H"):
        for cell in ws[col][1:]:
            if isinstance(cell.value, dt.date):
                cell.number_format = "DD.MM.YYYY"
    wb.save(path)
    return len(data)


# ---------------------------------------------------------------------------
# 2. Сотрудники (JSON)
# ---------------------------------------------------------------------------

def make_employees(path, rows=300):
    departments = ["Бухгалтерия", "IT", "Продажи", "Склад", "HR"]
    data = []
    for i in range(rows):
        gender = random.choice(["М", "Ж"])
        last = random.choice(LAST_NAMES) + ("а" if gender == "Ж" else "")
        hire = random_date(2000) - dt.timedelta(days=2000)
        data.append({
            "employee_id": 500 + i,
            "full_name": f"{last} {random.choice(FIRST_NAMES)}",
            "email": f"employee{i}@company.ru",
            "age": random.randint(20, 64),
            "gender": gender,
            "department": random.choice(departments),
            "salary": random.randint(45, 250) * 1000,
            "hire_date": hire.isoformat(),
            "contract_end": (hire + dt.timedelta(days=random.randint(365, 1500))).isoformat(),
            "address": {"city": random.choice(CITIES), "zip": str(random.randint(100000, 299999))},
        })

    used = set()
    def take(n):
        chosen = pick_rows(rows, n, used)
        used.update(chosen)
        return chosen

    for i in take(10):
        data[i]["email"] = None                              # пропуск
    for i in take(4):
        data[i]["email"] = "нет почты"                       # неверный email
    for i in take(3):
        data[i]["age"] = random.choice([-3, 150, 212])       # возраст вне диапазона
    for i in take(2):
        data[i]["gender"] = "X"                              # недопустимый пол
    for i in take(3):
        data[i]["salary"] = "по договорённости"              # текст вместо числа
    for i in take(4):
        hire = dt.date.fromisoformat(data[i]["hire_date"])
        data[i]["contract_end"] = (hire - dt.timedelta(days=30)).isoformat()  # конец раньше начала
    for i in take(2):
        data[i]["hire_date"] = "2024-13-40"                  # несуществующая дата
    for i in take(8):
        data[i]["address"]["city"] = None                    # пропуск во вложенном поле
    for i in take(3):
        data[i]["employee_id"] = data[i - 1]["employee_id"]  # повтор табельного номера

    data.append(json.loads(json.dumps(data[15])))            # полный дубль сотрудника

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data)


# ---------------------------------------------------------------------------
# 3. Выгрузка как из 1С (CSV, ";", Windows-1251, запятая в дробях)
# ---------------------------------------------------------------------------

def money(value):
    """12345.5 -> '12345,50' (так пишет 1С)."""
    return f"{value:.2f}".replace(".", ",")


def make_transactions_1c(path, rows=400):
    header = ["Номер", "Контрагент", "Цена", "Количество", "Итого",
              "Дата создания", "Дата закрытия", "Вид операции"]
    kinds = ["Поступление", "Реализация", "Возврат"]
    data = []
    for i in range(rows):
        price = round(random.uniform(100, 20000), 2)
        quantity = random.randint(1, 20)
        created = random_date()
        closed = created + dt.timedelta(days=random.randint(0, 14))
        data.append([
            f"ТР-{1000 + i}",
            f"ООО «{random.choice(LAST_NAMES)} и партнёры»",
            money(price),
            str(quantity),
            money(price * quantity),
            created.strftime("%d.%m.%Y"),
            closed.strftime("%d.%m.%Y"),
            random.choice(kinds),
        ])

    used = set()
    def take(n):
        chosen = pick_rows(rows, n, used)
        used.update(chosen)
        return chosen

    for i in take(12):
        data[i][1] = ""                                      # пустой контрагент
    for i in take(5):
        data[i][2] = "-" + data[i][2]                        # отрицательная цена
        data[i][4] = "-" + data[i][4]
    for i in take(6):
        total = float(data[i][4].replace(",", "."))
        data[i][4] = money(total + 500)                      # итог не сходится
    for i in take(5):
        created = dt.datetime.strptime(data[i][5], "%d.%m.%Y").date()
        data[i][6] = (created - dt.timedelta(days=5)).strftime("%d.%m.%Y")  # закрыта раньше создания
    for i in take(3):
        data[i][5] = "30.02.2025"                            # несуществующая дата
    for i in take(3):
        data[i][3] = "много"                                 # текст вместо числа
    for i in take(4):
        data[i][0] = data[i - 1][0]                          # повтор номера документа

    data += [list(data[10]), list(data[200])]                 # 2 полностью одинаковые строки

    with open(path, "w", newline="", encoding="cp1251") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(data)
    return len(data)


# ---------------------------------------------------------------------------
# 4. Чистый файл без ошибок (CSV)
# ---------------------------------------------------------------------------

def make_clean(path, rows=200):
    categories = ["Электроника", "Аксессуары", "Офис"]
    data = []
    for i in range(rows):
        product, price = random.choice(PRODUCTS)
        quantity = random.randint(1, 10)
        start = random_date()
        data.append({
            "id": i + 1,
            "product": product,
            "category": random.choice(categories),
            "price": price,
            "quantity": quantity,
            "total": price * quantity,
            "manager_email": f"manager{i % 7 + 1}@shop.ru",
            "start_date": start.strftime("%d.%m.%Y"),
            "end_date": (start + dt.timedelta(days=random.randint(1, 30))).strftime("%d.%m.%Y"),
        })

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    return len(data)


if __name__ == "__main__":
    files = [
        ("test_data/demo_orders.xlsx", make_orders),
        ("test_data/demo_employees.json", make_employees),
        ("test_data/demo_transactions_1c.csv", make_transactions_1c),
        ("test_data/demo_clean.csv", make_clean),
    ]
    for path, make in files:
        count = make(path)
        print(f"Готово: {path} ({count} строк)")
