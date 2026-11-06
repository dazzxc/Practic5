from fastapi import APIRouter

from app.schemas.report import Report
from app.services.report_service import generate_report

router = APIRouter()


@router.get("/get-report/{report_id}", response_model=Report)
def get_report(report_id: str):
    return generate_report(report_id)