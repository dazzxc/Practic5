from fastapi import HTTPException

from app.schemas.report import Report
from app.services.report_registry import get_report


def generate_report(report_id: str) -> Report:
    """Возвращает сохранённый отчёт по его id (для страницы прошлого отчёта)."""
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return Report(**report)
