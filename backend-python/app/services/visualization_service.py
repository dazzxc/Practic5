from fastapi import HTTPException

from app.schemas.visualization import VisualizationResponse


def generate_visualization(report_id: str) -> VisualizationResponse:
    raise HTTPException(
        status_code=501,
        detail=f"Visualization module is not connected yet: {report_id}"
    )