import csv
import chardet
import magic
import pandas as pd
from .base import BaseLoader
from .models import LoadResult, LoadMetadata


class CSVLoader(BaseLoader):
    def __init__(self, max_size_mb: float = 100.0):
        super().__init__(max_size_mb=max_size_mb)

    def _detect_encoding(self, file_path: str) -> str:
        """Автоопределение кодировки по первым 100KB файла"""
        with open(file_path, 'rb') as f:
            raw_data = f.read(100 * 1024)
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'

    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Автоопределение разделителя"""
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            sample = f.read(4096)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
                return dialect.delimiter
            except csv.Error:
                return ','  # Fallback на запятую

    def load(self, file_path: str, chunksize: int = 10000) -> LoadResult:
        file_size = self._validate_file(file_path, expected_mime_prefix='text/')
        encoding = self._detect_encoding(file_path)
        delimiter = self._detect_delimiter(file_path, encoding)
        
        warnings: list[str] = []
        try:
            # Чтение с чанками для контроля памяти, затем конкатенация
            chunks: list[pd.DataFrame] = []
            for chunk in pd.read_csv(file_path, sep=delimiter, encoding=encoding, 
                                     chunksize=chunksize, low_memory=False):
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
        except pd.errors.EmptyDataError:
            raise ValueError("CSV файл пуст")
        except UnicodeDecodeError as e:
            warnings.append(f"Проблемы с кодировкой: {e}. Использован fallback utf-8 с заменой ошибок.")
            df = pd.read_csv(file_path, sep=delimiter, encoding='utf-8', errors='replace')

        # Формирование схемы
        schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        metadata = LoadMetadata(
            file_name=file_path.split('/')[-1],
            mime_type=magic.from_file(file_path, mime=True),
            encoding=encoding,
            delimiter=delimiter,
            row_count=len(df),
            column_count=len(df.columns),
            schema=schema,
            file_size_bytes=file_size,
            is_chunked=chunksize < len(df),
            warnings=warnings
        )
        
        return LoadResult(df=df, metadata=metadata)
