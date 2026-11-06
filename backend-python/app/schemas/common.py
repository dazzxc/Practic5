from pydantic import BaseModel
from typing import Optional


class Issue(BaseModel):
    type: str
    column: Optional[str] = None
    description: str
    count: int = 0
    recommendation: Optional[str] = None