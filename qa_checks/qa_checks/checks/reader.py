"""
Чтение файла ПО ЧАСТЯМ (чанками).

Зачем: файл на 10 миллионов строк не влезет в память целиком.
Поэтому читаем, например, по 15 000 строк, проверяем их и выкидываем из памяти.

Поддерживаются: .csv и .xlsx
(старый формат .xls не поддерживается - его надо пересохранить в .xlsx)

ВАЖНО: номера строк (index) сквозные. Если в первом чанке строки 0..99999,
то во втором будут 100000..199999. Так в отчёте будут правильные номера строк.
"""

import os

import pandas as pd

DEFAULT_CHUNK_SIZE = 15_000  # сколько строк читать за один раз (хороший баланс скорости и памяти)


def detect_encoding(path):
    """Пробует прочитать начало файла в UTF-8, если не вышло - значит Windows-1251."""
    with open(path, "rb") as f:
        sample = f.read(1_000_000)  # первый 1 МБ
    try:
        sample.decode("utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError as e:
        # Ошибка могла быть просто из-за того, что мы обрезали букву на границе 1 МБ
        if e.start >= len(sample) - 3:
            return "utf-8-sig"
        return "cp1251"


def detect_separator(path, encoding):
    """Смотрит на первую строку и выбирает самый частый разделитель."""
    with open(path, encoding=encoding, errors="replace") as f:
        first_line = f.readline()
    candidates = [",", ";", "\t", "|"]
    return max(candidates, key=first_line.count)


def read_csv_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Читает CSV по частям. Сам определяет кодировку и разделитель."""
    encoding = detect_encoding(path)
    separator = detect_separator(path, encoding)

    # dtype=str - всё читаем как текст, чтобы "abc" в числовой колонке не ломал чтение.
    # Значения вроде "NA", "null", "NaN" pandas сам считает пропусками - для нас это правильно.
    reader = pd.read_csv(path, dtype=str, chunksize=chunk_size,
                         encoding=encoding, sep=separator)
    for chunk in reader:
        yield chunk


def read_excel_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE, sheet_name=None):
    """
    Читает .xlsx по частям.

    pandas.read_excel не умеет читать по частям, поэтому используем openpyxl
    в режиме read_only - он читает файл построчно и не грузит его в память целиком.
    """
    from openpyxl import load_workbook

    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[sheet_name] if sheet_name else workbook.active

    rows = sheet.iter_rows(values_only=True)
    header = next(rows, None)  # первая строка - названия колонок
    if header is None:
        workbook.close()
        return

    header = [str(h) if h is not None else f"column_{i}" for i, h in enumerate(header)]

    buffer = []    # сюда копим строки, пока не наберётся chunk_size
    start = 0      # номер первой строки текущего чанка

    for row in rows:
        buffer.append(row)
        if len(buffer) == chunk_size:
            yield _make_chunk(buffer, header, start)
            start += len(buffer)
            buffer = []

    if buffer:  # остаток в конце файла
        yield _make_chunk(buffer, header, start)

    workbook.close()


def _make_chunk(rows, header, start):
    """Превращает список строк в DataFrame со сквозными номерами строк."""
    # Если в строке ячеек меньше, чем колонок, - дополняем пустыми
    width = len(header)
    rows = [list(r[:width]) + [None] * (width - len(r)) for r in rows]
    df = pd.DataFrame(rows, columns=header, dtype=object)
    df.index = range(start, start + len(df))
    return df


def read_in_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Выбирает нужный способ чтения по расширению файла."""
    extension = os.path.splitext(path)[1].lower()

    if extension in (".csv", ".txt"):
        return read_csv_chunks(path, chunk_size)
    if extension in (".xlsx", ".xlsm"):
        return read_excel_chunks(path, chunk_size)

    raise ValueError(f"Формат {extension} не поддерживается. Нужен .csv или .xlsx")
