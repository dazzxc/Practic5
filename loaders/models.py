from dataclasses import dataclass, field
import pandas as pd


@dataclass
class LoadMetadata:
    """сведения о файле"""
    file_name: str
    mime_type: str
    encoding: str | None
    delimiter: str | None  # только CSV
    row_count: int
    column_count: int
    schema: dict[str, str] 
    file_size_bytes: int
    is_chunked: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class LoadResult:
    """таблица + сведения"""
    df: pd.DataFrame
    metadata: LoadMetadata
