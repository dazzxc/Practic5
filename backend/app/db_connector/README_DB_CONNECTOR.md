
Инструкция

 📖 Инструкция: Модуль коннектора к БД (db_connector)

Этот модуль умеет подключаться к базам данных (SQLite/PostgreSQL), показывать список таблиц и забирать из них данные в виде таблиц pandas (DataFrame) для проверки качества.

 Шаг 1: Подготовка окружения (venv)

В Python принято работать в изолированном "виртуальном окружении" (venv), чтобы библиотеки одного проекта не ломали другой.
1. Открой терминал в папке проекта.
2. Создай окружение (если его еще нет): `python -m venv venv`
3. Активируй его:
   - На Windows: `venv\Scripts\activate`
   - На Mac/Linux: `source venv/bin/activate`
   *(В начале строки терминала появится `(venv)` — значит, всё получилось).*

Шаг 2: Установка библиотек

Находясь в активированном окружении `(venv)`, в терминале выполни:
pip install -r requirements.txt


Шаг 3: Настройка секретов (файл .env)

Пароли нельзя хранить в коде. Они хранятся в файле `.env`, который не попадает в Git.
1. Скопируй файл-шаблон .env.example и переименуй копию в .env
2. Открой .env и впиши свои данные:
```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=твой_секретный_ключ_123
DEBUG=True
```

Шаг 4: Как использовать код
```python
from app.loaders.db_connector import DBConnector

db = DBConnector()       # Читает настройки из .env
db.connect()             # Подключается к базе

# Получить список таблиц
tables = db.get_tables() 
print(tables)            # Например: ['users', 'orders']

# Прочитать таблицу в DataFrame (limit защищает от зависания на больших данных)
df = db.read_table("users", limit=100) 
print(df.head())
```

Шаг 5: Шифрование паролей
Если нужно сохранить пароль пользователя в базу, используй модуль crypto:
```python
from app.crypto import crypto
encrypted = crypto.encrypt("my_password")
decrypted = crypto.decrypt(encrypted)
```

Шаг 6: Проверка работоспособности (тесты)
Чтобы убедиться, что всё работает, запусти тесты:
```bash
pytest tests/test_db_connector.py -v
```
Если видишь 2 зеленых `PASSED` — всё отлично.
```

---

