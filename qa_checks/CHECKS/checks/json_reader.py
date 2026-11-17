"""чтение JSON кусками"""

import json

import pandas as pd


def flatten(obj, prefix=""):
    """{"b": {"c": 2}} -> {"b.c": 2}"""
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
    """объекты -> DataFrame"""
    rows = [flatten(r) if isinstance(r, dict) else {"value": r} for r in records]
    # object, чтобы 7 не стало 7.0
    df = pd.DataFrame(rows, dtype=object)
    df.index = range(start, start + len(df))
    return df


def _in_chunks(objects, chunk_size):
    """пачки по chunk_size"""
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
    """первый символ без BOM"""
    with open(path, encoding="utf-8-sig") as f:
        while True:
            ch = f.read(1)
            if ch == "" or not ch.isspace():
                return ch


def _looks_like_json_lines(path):
    """это JSON Lines?"""
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
    """JSON Lines построчно"""
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
    """ключ со списком"""
    import ijson

    with open(path, "rb") as f:
        for prefix, event, _ in ijson.parse(f):
            # ключ верхнего уровня
            if event == "start_array" and prefix and "." not in prefix:
                return prefix
    return None


def _read_with_ijson(path, prefix):
    """по одному объекту"""
    import ijson

    with open(path, "rb") as f:
        # float, а не Decimal
        for obj in ijson.items(f, prefix, use_float=True):
            yield obj


def read_json_chunks(path, chunk_size):
    """определяем вид и читаем"""
    first = _first_char(path)

    if first == "[":
        # список объектов
        objects = _read_with_ijson(path, "item")

    elif first == "{":
        if _looks_like_json_lines(path):
            # JSON Lines
            objects = _read_json_lines(path)
        else:
            # обёртка {"data": [...]}
            key = _find_list_key(path)
            if key is None:
                # одна запись
                objects = _read_with_ijson(path, "")
            else:
                objects = _read_with_ijson(path, f"{key}.item")

    elif first == "":
        return  # пустой файл

    else:
        raise ValueError("Файл не похож на JSON: он должен начинаться с [ или {")

    yield from _in_chunks(objects, chunk_size)
