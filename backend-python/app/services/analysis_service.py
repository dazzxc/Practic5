from fastapi import HTTPException

from app.schemas.analysis import AnalysisRequest
from app.schemas.analysis_response import AnalysisResponse

from app.services.dataset_registry import get_dataset


def run_data_analysis(request: AnalysisRequest) -> AnalysisResponse:
    dataset = get_dataset(request.dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    file_path = dataset["file_path"]

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset file does not exist"
        )

    raise HTTPException(
        status_code=501,
        detail="Data quality engine is not connected yet"
    )