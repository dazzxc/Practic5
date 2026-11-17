from fastapi import HTTPException

from app.schemas.report import Report
from app.services.report_registry import get_report


def generate_report(report_id: str) -> Report:
    """отчёт по id"""
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return Report(**report)
