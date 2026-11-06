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