import pytest
import pandas as pd
import os
import tempfile
from loaders import CSVLoader, JSONLoader


@pytest.fixture
def temp_csv_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        f.write("id;name;age\n1;Alice;30\n2;Bob;25\n")
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def temp_jsonl_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        f.write('{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n')
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def temp_invalid_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is not a CSV or JSON")
        path = f.name
    yield path
    os.unlink(path)


def test_csv_loader_success(temp_csv_file):
    loader = CSVLoader(max_size_mb=1.0)
    result = loader.load(temp_csv_file)

    assert isinstance(result.df, pd.DataFrame)
    assert result.metadata.row_count == 2
    assert result.metadata.column_count == 3
    assert result.metadata.delimiter == ';'
    assert 'utf' in result.metadata.encoding.lower()
    assert result.metadata.mime_type == 'text/plain'


def test_json_loader_success(temp_jsonl_file):
    loader = JSONLoader(max_size_mb=1.0)
    result = loader.load(temp_jsonl_file)

    assert isinstance(result.df, pd.DataFrame)
    assert result.metadata.row_count == 2
    assert 'id' in result.df.columns
    assert result.metadata.mime_type in ['application/json', 'text/plain']


def test_size_limit_exceeded(temp_csv_file):
    loader = CSVLoader(max_size_mb=0.0001)  # лимит около 100 байт
    with pytest.raises(ValueError, match="превышает лимит размера"):
        loader.load(temp_csv_file)


def test_invalid_mime_type(temp_invalid_file):
    loader = CSVLoader(max_size_mb=1.0)
    with pytest.raises(ValueError, match="Неверный MIME-тип"):
        loader.load(temp_invalid_file)


def test_file_not_found():
    loader = CSVLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("non_existent_file.csv")
