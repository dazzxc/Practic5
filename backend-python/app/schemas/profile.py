from pydantic import BaseModel


class DataProfile(BaseModel):
    file_name: str
    file_type: str
    rows_count: int
    columns_count: int
    columns: list[str]
    missing_values: int = 0
    duplicates: int = 0
    invalid_values: int = 0
    inconsistencies: int = 0
