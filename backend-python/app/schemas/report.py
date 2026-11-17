from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import Issue
from app.schemas.profile import DataProfile


class Report(BaseModel):
    report_id: str
    status: str
    profile: DataProfile
    issues: list[Issue]
    total_issues: int = 0
    recommendations: list[str] = Field(default_factory=list)
    # правила и автоподбор
    applied_rules: Optional[dict[str, Any]] = None
    auto_rules: bool = False
    # время проверки
    created_at: Optional[str] = None
