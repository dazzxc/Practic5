from fastapi import APIRouter

from app.schemas.visualization import VisualizationResponse
from app.services.visualization_service import generate_visualization

router = APIRouter()


@router.get(
    "/get-visualization/{report_id}",
    response_model=VisualizationResponse
)
def get_visualization(report_id: str):
    return generate_visualization(report_id)