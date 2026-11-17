"""чтение файла кусками"""

import os

import pandas as pd

DEFAULT_CHUNK_SIZE = 15_000  # строк за раз


def detect_encoding(path):
    """UTF-8 или Windows-1251"""
    with open(path, "rb") as f:
        sample = f.read(1_000_000)  # 1 МБ
    try:
        sample.decode("utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError as e:
        # обрезанная буква на границе
        if e.start >= len(sample) - 3:
            return "utf-8-sig"
        return "cp1251"


def detect_separator(path, encoding):
    """самый частый разделитель"""
    with open(path, encoding=encoding, errors="replace") as f:
        first_line = f.readline()
    candidates = [",", ";", "\t", "|"]
    return max(candidates, key=first_line.count)


def read_csv_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE):
    """CSV кусками"""
    encoding = detect_encoding(path)
    separator = detect_separator(path, encoding)

    # всё как текст
    reader = pd.read_csv(path, dtype=str, chunksize=chunk_size,
                         encoding=encoding, sep=separator)
    for chunk in reader:
        yield chunk


def read_excel_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE, sheet_name=None):
    """.xlsx кусками через openpyxl"""
    from openpyxl import load_workbook

    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[sheet_name] if sheet_name else workbook.active

    rows = sheet.iter_rows(values_only=True)
    header = next(rows, None)  # заголовки
    if header is None:
        workbook.close()
        return

    header = [str(h) if h is not None else f"column_{i}" for i, h in enumerate(header)]

    buffer = []  # буфер строк
    start = 0    # номер первой строки куска

    for row in rows:
        buffer.append(row)
        if len(buffer) == chunk_size:
            yield _make_chunk(buffer, header, start)
            start += len(buffer)
            buffer = []

    if buffer:  # хвост
        yield _make_chunk(buffer, header, start)

    workbook.close()


def _make_chunk(rows, header, start):
    """строки -> DataFrame"""
    # добиваем пустыми
    width = len(header)
    rows = [list(r[:width]) + [None] * (width - len(r)) for r in rows]
    df = pd.DataFrame(rows, columns=header, dtype=object)
    df.index = range(start, start + len(df))
    return df


def read_in_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE):
    """выбор по расширению"""
    extension = os.path.splitext(path)[1].lower()

    if extension in (".csv", ".txt"):
        return read_csv_chunks(path, chunk_size)
    if extension in (".xlsx", ".xlsm"):
        return read_excel_chunks(path, chunk_size)
    if extension in (".json", ".jsonl", ".ndjson"):
        from checks.json_reader import read_json_chunks
        return read_json_chunks(path, chunk_size)

    raise ValueError(f"Формат {extension} не поддерживается. Нужен .csv, .xlsx или .json")
