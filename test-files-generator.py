import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_large_datasets():
    print("📦 Запуск генерации больших демонстрационных датасетов...")
    random.seed(42)  # Фиксируем сид для воспроизводимости данных
    np.random.seed(42)

    # -------------------------------------------------------------
    # ФАЙЛ 1: "large_users_quality.csv" (~10 000 строк)
    # -------------------------------------------------------------
    print("🔹 Генерируем базу пользователей (10,000 строк)...")
    size_users = 10000
    
    # Генерируем ID с умышленными дубликатами (около 3% повторов)
    user_ids = [100000 + i for i in range(size_users)]
    for _ in range(300):
        user_ids[random.randint(0, size_users-1)] = user_ids[random.randint(0, size_users-1)]
        
    # Списки для генерации имен
    first_names = ["Иван", "Петр", "Сергей", "Анна", "Мария", "Елена", "Алексей", "Ольга"]
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Попов", "Смирнов", "Васильев"]
    
    names = [f"{random.choice(last_names)} {random.choice(first_names)}" for _ in range(size_users)]
    # Закладываем 2% явных пропусков (Null) и 1% неявных (пустые строки)
    for _ in range(200): names[random.randint(0, size_users-1)] = None
    for _ in range(100): names[random.randint(0, size_users-1)] = "   "

    # Возраст с аномалиями (выбросы, отрицательные числа)
    ages = np.random.randint(18, 70, size=size_users).astype(object)
    for _ in range(150): ages[random.randint(0, size_users-1)] = None           # Пропуски
    for _ in range(50):  ages[random.randint(0, size_users-1)] = -15            # Отрицательный возраст
    for _ in range(50):  ages[random.randint(0, size_users-1)] = 150            # Нереальный возраст (выброс)
    for _ in range(50):  ages[random.randint(0, size_users-1)] = "СтроковоеЗначение" # Ошибка типа данных

    df_users = pd.DataFrame({
        "user_id": user_ids,
        "fio": names,
        "age": ages,
        "country": [random.choice(["Russia", "Belarus", "Kazakhstan", None]) for _ in range(size_users)]
    })
    
    df_users.to_csv("large_users_quality.csv", index=False)
    print("✅ Создан файл: large_users_quality.csv")

    # -------------------------------------------------------------
    # ФАЙЛ 2: "large_transactions_quality.csv" (~50 000 строк)
    # -------------------------------------------------------------
    print("🔹 Генерируем лог транзакций (50,000 строк)...")
    size_tx = 50000
    
    tx_ids = [5000000 + i for i in range(size_tx)]
    # Полные дубликаты строк (симулируем сбой логгера — 500 строк продублированы целиком)
    cust_ids = [random.randint(100000, 110000) for _ in range(size_tx)]
    
    # Суммы транзакций с пропусками и ошибками
    amounts = np.random.uniform(50.0, 95000.0, size=size_tx).astype(object)
    for _ in range(1000): amounts[random.randint(0, size_tx-1)] = None
    for _ in range(200):  amounts[random.randint(0, size_tx-1)] = -99.99

    # Даты для проверки логической согласованности
    base_date = datetime(2026, 1, 1)
    dates_start = [base_date + timedelta(minutes=random.randint(0, 500000)) for _ in range(size_tx)]
    dates_end = [d + timedelta(days=random.randint(1, 5)) for d in dates_start]
    
    # Ломаем логику дат у 400 транзакций (дата конца раньше даты начала)
    for _ in range(400):
        idx = random.randint(0, size_tx-1)
        dates_end[idx] = dates_start[idx] - timedelta(days=3)

    df_tx = pd.DataFrame({
        "transaction_id": tx_ids,
        "customer_id": cust_ids,
        "amount": amounts,
        "created_at": [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates_start],
        "completed_at": [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates_end]
    })

    # Добавляем 500 полных дубликатов строк в самый конец
    df_tx = pd.concat([df_tx, df_tx.head(500)], ignore_index=True)
    
    df_tx.to_csv("large_transactions_quality.csv", index=False)
    print(f"✅ Создан файл: large_transactions_quality.csv ({len(df_tx)} строк)")

if __name__ == "__main__":
    generate_large_datasets()