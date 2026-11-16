from dataclasses import dataclass, field
import pandas as pd


@dataclass
class LoadMetadata:
    """Что узнали о файле при загрузке."""
    file_name: str
    mime_type: str
    encoding: str | None
    delimiter: str | None  # Только для CSV
    row_count: int
    column_count: int
    schema: dict[str, str]  # {column_name: dtype_str}
    file_size_bytes: int
    is_chunked: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class LoadResult:
    """Таблица + сведения о файле."""
    df: pd.DataFrame
    metadata: LoadMetadata
