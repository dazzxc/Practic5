from fastapi import APIRouter
from app.schemas.analysis import AnalysisRequest, SuggestRequest
from app.schemas.report import Report
from app.services.analysis_service import run_data_analysis, suggest_file_rules

router = APIRouter()

@router.post("/run-check", response_model=Report)
def run_check(request: AnalysisRequest):
    return run_data_analysis(request)


@router.post("/suggest-rules")
def suggest_rules(request: SuggestRequest):
    return suggest_file_rules(request.dataset_id)
