from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    status: str
    message: str
    task_id: str | None = None