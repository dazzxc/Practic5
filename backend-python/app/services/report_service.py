from fastapi import HTTPException

from app.schemas.report import Report


def generate_report(report_id: str) -> Report:
    raise HTTPException(
        status_code=501,
        detail=f"Report generation module is not connected yet: {report_id}"
    )