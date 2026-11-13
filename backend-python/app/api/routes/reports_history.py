from fastapi import APIRouter
from app.services.report_registry import get_all_reports

router = APIRouter()

@router.get("/history")
def get_reports_history():
    return get_all_reports()