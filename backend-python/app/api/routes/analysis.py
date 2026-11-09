from fastapi import APIRouter
from app.schemas.analysis import AnalysisRequest
from app.schemas.report import Report
from app.services.analysis_service import run_data_analysis

router = APIRouter()

@router.post("/run-check", response_model=Report)
def run_check(request: AnalysisRequest):
    return run_data_analysis(request)