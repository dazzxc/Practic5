from pydantic import BaseModel
from typing import List, Dict, Any


class Issue(BaseModel):
    check_type: str
    column: str
    severity: str  # low, medium, high
    message: str
    count: int
    sample: List[Dict[str, Any]]


class QualityReport(BaseModel):
    timestamp: str
    total_rows: int
    total_columns: int
    metrics: Dict[str, float]
    issues: List[Issue]