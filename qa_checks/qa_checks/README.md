# Проверки качества данных (Человек 4)

Проверяет CSV, Excel (.xlsx) и JSON **любого размера**: файл читается по частям (чанками),
поэтому целиком в память не загружается. Без pandera, всё написано на pandas.

## Установка
```
pip install -r requirements.txt
```

## Запуск
```
python run.py                              # маленький тестовый файл
python run.py мой_файл.csv                 # свой CSV
python run.py мой_файл.xlsx                # свой Excel
python run.py мой_файл.json                # свой JSON (или .jsonl)
python run.py мой_файл.csv 50000           # свой размер чанка (по умолчанию 15 000 строк)
```

## Проверить на большом файле
```
python make_big_file.py 1000000            # создаст test_data/big.csv на 1 млн строк
python make_big_file.py 200000 xlsx        # создаст test_data/big.xlsx на 200 тыс. строк
python make_big_file.py 500000 json        # создаст test_data/big.json на 500 тыс. записей
python run.py test_data/big.csv
```

## Автотесты
```
pytest
```

## Структура
```
checks/
  reader.py       - чтение CSV/Excel по частям (кодировка и разделитель определяются сами)
  json_reader.py  - чтение JSON по частям (список, JSON Lines, обёртка {"data": [...]})
  issue.py        - общий формат проблемы (Issue) и общие помощники
  missing.py      - 1. пропуски
  duplicates.py   - 2. дубликаты (помнит строки из прошлых чанков)
  invalid.py      - 3. некорректные значения
  consistency.py  - 4. несогласованности
  __init__.py     - check_file() и run_all_checks()
test_data/clients.csv  - маленький файл со специальными ошибками
test_data/clients.json - те же данные в JSON (плюс вложенное поле address.city)
tests/                - автотесты
run.py                - ручной запуск
make_big_file.py      - генератор большого файла
```

## Как подключить к бэкенду (для Человека 1)
```python
from checks import check_file

result = check_file("путь/к/файлу.csv", config, on_progress=lambda n: print(n))
# result = {"total_rows": ..., "columns": [...], "issues": [...]}
```
`on_progress` вызывается после каждого чанка с числом проверенных строк - это для прогресс-бара.

## Какой JSON поддерживается
- список объектов: `[{"id": 1}, {"id": 2}]`
- JSON Lines (по объекту на строку): `.jsonl` или `.json`
- обёртка: `{"data": [{"id": 1}, ...]}`, ключ со списком находится сам
- вложенные объекты становятся колонками через точку: `{"address": {"city": "..."}}` -> `address.city`
- если поле есть не у всех записей, у остальных оно считается пропуском

## Ограничения
- Старый формат `.xls` не поддерживается: пересохраните файл в `.xlsx`.
- Excel читается медленнее CSV (примерно 8 тыс. строк в секунду против 100 тыс.).
- Для поиска дублей программа хранит 8 байт на строку: 100 млн строк - около 800 МБ.
