"""
Чтение файла кусками.

Файл на 10 млн строк в память целиком не влезет, поэтому читаем по 15 000 строк.
Умеем .csv, .xlsx и .json/.jsonl (JSON - в json_reader.py). Старый .xls не умеем,
его надо пересохранить в .xlsx.

Номера строк сквозные: в первом куске 0..14999, во втором 15000..29999 и так далее.
Так в отчёте будут настоящие номера строк.
"""

import os

import pandas as pd

DEFAULT_CHUNK_SIZE = 15_000  # строк за раз: и быстро, и памяти немного


def detect_encoding(path):
    """Пробуем прочитать начало как UTF-8. Не вышло - значит Windows-1251."""
    with open(path, "rb") as f:
        sample = f.read(1_000_000)  # первый 1 МБ
    try:
        sample.decode("utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError as e:
        # Может, мы просто разрезали букву на границе 1 МБ - это не считается
        if e.start >= len(sample) - 3:
            return "utf-8-sig"
        return "cp1251"


def detect_separator(path, encoding):
    """Какой разделитель чаще всего в первой строке, тот и берём."""
    with open(path, encoding=encoding, errors="replace") as f:
        first_line = f.readline()
    candidates = [",", ";", "\t", "|"]
    return max(candidates, key=first_line.count)


def read_csv_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE):
    """CSV кусками. Кодировку и разделитель определяем сами."""
    encoding = detect_encoding(path)
    separator = detect_separator(path, encoding)

    # dtype=str - читаем всё как текст, чтобы "abc" в колонке с числами ничего не сломал.
    # "NA", "null", "NaN" pandas сам считает пустыми - нам так и надо.
    reader = pd.read_csv(path, dtype=str, chunksize=chunk_size,
                         encoding=encoding, sep=separator)
    for chunk in reader:
        yield chunk


def read_excel_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE, sheet_name=None):
    """
    .xlsx кусками.
    pandas так не умеет, поэтому берём openpyxl в режиме read_only - он идёт по строкам
    и не грузит весь файл в память.
    """
    from openpyxl import load_workbook

    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[sheet_name] if sheet_name else workbook.active

    rows = sheet.iter_rows(values_only=True)
    header = next(rows, None)  # первая строка - заголовки
    if header is None:
        workbook.close()
        return

    header = [str(h) if h is not None else f"column_{i}" for i, h in enumerate(header)]

    buffer = []  # копим строки, пока не наберётся chunk_size
    start = 0    # номер первой строки в текущем куске

    for row in rows:
        buffer.append(row)
        if len(buffer) == chunk_size:
            yield _make_chunk(buffer, header, start)
            start += len(buffer)
            buffer = []

    if buffer:  # хвост файла
        yield _make_chunk(buffer, header, start)

    workbook.close()


def _make_chunk(rows, header, start):
    """Строки -> DataFrame со сквозными номерами."""
    # Если ячеек меньше, чем колонок, добиваем пустыми
    width = len(header)
    rows = [list(r[:width]) + [None] * (width - len(r)) for r in rows]
    df = pd.DataFrame(rows, columns=header, dtype=object)
    df.index = range(start, start + len(df))
    return df


def read_in_chunks(path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Выбираем, как читать, по расширению файла."""
    extension = os.path.splitext(path)[1].lower()

    if extension in (".csv", ".txt"):
        return read_csv_chunks(path, chunk_size)
    if extension in (".xlsx", ".xlsm"):
        return read_excel_chunks(path, chunk_size)
    if extension in (".json", ".jsonl", ".ndjson"):
        from checks.json_reader import read_json_chunks
        return read_json_chunks(path, chunk_size)

    raise ValueError(f"Формат {extension} не поддерживается. Нужен .csv, .xlsx или .json")
