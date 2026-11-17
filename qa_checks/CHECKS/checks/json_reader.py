"""
Чтение JSON кусками.

Понимаем 3 вида JSON:

1) Список объектов (так чаще всего):
   [
     {"id": 1, "name": "Аня"},
     {"id": 2, "name": "Петя"}
   ]

2) JSON Lines (.jsonl) - по одному объекту на строку:
   {"id": 1, "name": "Аня"}
   {"id": 2, "name": "Петя"}

3) Обёртка - список лежит внутри объекта:
   {"data": [ {"id": 1}, {"id": 2} ]}

Вложенные объекты становятся колонками через точку:
   {"address": {"city": "Москва"}}  ->  колонка "address.city"

json.load() грузит весь файл сразу, на большом файле не хватит памяти.
Поэтому для 1 и 3 берём ijson: он читает понемногу и отдаёт по одному объекту.
"""

import json

import pandas as pd


def flatten(obj, prefix=""):
    """
    Делает вложенный словарь плоским.
    {"a": 1, "b": {"c": 2}}  ->  {"a": 1, "b.c": 2}
    Списки оставляем как есть (превращаем в текст), их в колонки не раскладываем.
    """
    flat = {}
    for key, value in obj.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(flatten(value, prefix=name + "."))
        elif isinstance(value, list):
            flat[name] = json.dumps(value, ensure_ascii=False)
        else:
            flat[name] = value
    return flat


def _to_dataframe(records, start):
    """Объекты -> DataFrame со сквозными номерами строк."""
    rows = [flatten(r) if isinstance(r, dict) else {"value": r} for r in records]
    # dtype=object, чтобы 7 не превратилось в 7.0, если где-то пусто
    df = pd.DataFrame(rows, dtype=object)
    df.index = range(start, start + len(df))
    return df


def _in_chunks(objects, chunk_size):
    """Складываем объекты в пачки по chunk_size."""
    buffer = []
    start = 0
    for obj in objects:
        buffer.append(obj)
        if len(buffer) == chunk_size:
            yield _to_dataframe(buffer, start)
            start += len(buffer)
            buffer = []
    if buffer:
        yield _to_dataframe(buffer, start)


def _first_char(path):
    """Первый символ файла без пробелов и BOM."""
    with open(path, encoding="utf-8-sig") as f:
        while True:
            ch = f.read(1)
            if ch == "" or not ch.isspace():
                return ch


def _looks_like_json_lines(path):
    """
    JSON Lines: в первой строке целый объект, а дальше есть ещё строки.
    Обычный JSON-объект на одной строке не считается JSON Lines.
    """
    with open(path, encoding="utf-8-sig") as f:
        first = f.readline().strip()
        second = f.readline().strip()
    if not first or not second:
        return False
    try:
        json.loads(first)
        return True
    except json.JSONDecodeError:
        return False


def _read_json_lines(path):
    """JSON Lines построчно."""
    with open(path, encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Ошибка в JSON на строке {line_number}: {e.msg}") from None


def _find_list_key(path):
    """
    Для обёртки {"data": [...]} ищет, в каком ключе лежит список.
    Читает файл с начала, пока не встретит первый список на верхнем уровне.
    """
    import ijson

    with open(path, "rb") as f:
        for prefix, event, _ in ijson.parse(f):
            # prefix без точек = ключ верхнего уровня, например "data"
            if event == "start_array" and prefix and "." not in prefix:
                return prefix
    return None


def _read_with_ijson(path, prefix):
    """По одному объекту, не загружая весь файл."""
    import ijson

    with open(path, "rb") as f:
        # use_float=True, чтобы дроби были обычными float, а не Decimal
        for obj in ijson.items(f, prefix, use_float=True):
            yield obj


def read_json_chunks(path, chunk_size):
    """Понимаем, какой это JSON, и читаем кусками."""
    first = _first_char(path)

    if first == "[":
        # Вид 1: список объектов
        objects = _read_with_ijson(path, "item")

    elif first == "{":
        if _looks_like_json_lines(path):
            # Вид 2: JSON Lines
            objects = _read_json_lines(path)
        else:
            # Вид 3: обёртка {"data": [...]}
            key = _find_list_key(path)
            if key is None:
                # Списка внутри нет - значит, это одна запись
                objects = _read_with_ijson(path, "")
            else:
                objects = _read_with_ijson(path, f"{key}.item")

    elif first == "":
        return  # пустой файл

    else:
        raise ValueError("Файл не похож на JSON: он должен начинаться с [ или {")

    yield from _in_chunks(objects, chunk_size)
