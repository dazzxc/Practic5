from pydantic import BaseModel, Field
from typing import Optional


class Issue(BaseModel):
    type: str
    # Группа ошибки: missing / duplicate / invalid / inconsistency
    category: str = "invalid"
    column: Optional[str] = None
    description: str
    count: int = 0
    percent: float = 0
    severity: str = "low"
    sample_rows: list[int] = Field(default_factory=list)
    recommendation: Optional[str] = None
