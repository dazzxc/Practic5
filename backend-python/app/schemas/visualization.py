from pydantic import BaseModel


class VisualizationResponse(BaseModel):
    report_id: str
    chart_type: str
    title: str
    labels: list[str]
    values: list[int | float]