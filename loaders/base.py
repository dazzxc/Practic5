import os
import magic
from abc import ABC, abstractmethod
from .models import LoadResult


class BaseLoader(ABC):
    def __init__(self, max_size_mb: float = 100.0):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)

    def _validate_file(self, file_path: str, expected_mime_prefix: str) -> int:
        """проверка файла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size > self.max_size_bytes:
            raise ValueError(f"Файл превышает лимит размера: {file_size} байт > {self.max_size_bytes} байт")

        mime_type = magic.from_file(file_path, mime=True)
        if not mime_type.startswith(expected_mime_prefix):
            raise ValueError(f"Неверный MIME-тип: ожидается {expected_mime_prefix}, получен {mime_type}")

        return file_size

    @abstractmethod
    def load(self, file_path: str, chunksize: int = 10000) -> LoadResult:
        pass
