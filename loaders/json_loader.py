import json
import chardet
import magic
import pandas as pd
from .base import BaseLoader
from .models import LoadResult, LoadMetadata


class JSONLoader(BaseLoader):
    def __init__(self, max_size_mb: float = 100.0):
        super().__init__(max_size_mb=max_size_mb)

    def _is_jsonl(self, file_path: str, encoding: str = 'utf-8') -> bool:
        """Проверка, является ли файл JSON Lines (по первой строке)"""
        with open(file_path, 'r', encoding=encoding) as f:
            first_line = f.readline().strip()
            try:
                json.loads(first_line)
                return True
            except json.JSONDecodeError:
                return False

    def load(self, file_path: str, chunksize: int = 10000) -> LoadResult:
        file_size = self._validate_file(file_path, expected_mime_prefix='application/')
        
        # Определяем кодировку (для JSON чаще всего utf-8, но проверим)
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024)
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

        is_jsonl = self._is_jsonl(file_path, encoding)
        warnings: list[str] = []

        try:
            if is_jsonl:
                # Чтение JSONL чанками
                chunks: list[pd.DataFrame] = []
                with open(file_path, 'r', encoding=encoding) as f:
                    current_chunk: list[dict] = []
                    for line in f:
                        current_chunk.append(json.loads(line))
                        if len(current_chunk) >= chunksize:
                            chunks.append(pd.DataFrame(current_chunk))
                            current_chunk = []
                    if current_chunk:
                        chunks.append(pd.DataFrame(current_chunk))
                df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
            else:
                # Чтение обычного JSON (массив объектов или один объект)
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        df = pd.DataFrame([data])
                    else:
                        raise TypeError("JSON должен быть массивом объектов или одним объектом")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON: {e}")

        schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        metadata = LoadMetadata(
            file_name=file_path.split('/')[-1],
            mime_type=magic.from_file(file_path, mime=True),
            encoding=encoding,
            delimiter=None,
            row_count=len(df),
            column_count=len(df.columns),
            schema=schema,
            file_size_bytes=file_size,
            is_chunked=is_jsonl and len(df) > chunksize,
            warnings=warnings
        )
        
        return LoadResult(df=df, metadata=metadata)
