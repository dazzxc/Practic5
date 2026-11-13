import sys
import uuid
from pathlib import Path
from fastapi import HTTPException

from app.schemas.analysis import AnalysisRequest
from app.schemas.report import Report
from app.schemas.profile import DataProfile
from app.schemas.common import Issue
from app.services.dataset_registry import get_dataset
from app.services.report_registry import save_report

# Прокладываем путь к папке qa_checks
current_dir = Path(__file__).resolve().parent
qa_checks_path = current_dir.parents[2] / "qa_checks" / "qa_checks"
sys.path.append(str(qa_checks_path))

try:
    from checks import check_file
except ImportError as e:
    raise RuntimeError(f"Не удалось импортировать check_file. Ошибка: {e}")

# Базовый конфиг (используется, если фронтенд ничего не передал)
DEFAULT_CONFIG = {
    "key_columns": ["id"],
    "invalid_rules": {
        "age": {"type": "number", "min": 0, "max": 120},
        "email": {"type": "email"},
        "start_date": {"type": "date", "format": "%d.%m.%Y"},
        "end_date": {"type": "date", "format": "%d.%m.%Y"},
        "gender": {"allowed": ["М", "Ж"]},
    },
    "consistency_rules": [
        {"rule": "dates_order", "start": "start_date", "end": "end_date", "format": "%d.%m.%Y"},
        {"rule": "total", "price": "price", "quantity": "quantity", "total": "total"},
    ],
}

def run_data_analysis(request: AnalysisRequest) -> Report:
    dataset = get_dataset(request.dataset_id)

    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset["file_path"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset file does not exist")

    # ВЫБИРАЕМ КОНФИГ: если фронтенд прислал свой - используем его, иначе дефолтный
    config_to_use = request.config if request.config else DEFAULT_CONFIG

    try:
        raw_result = check_file(str(file_path), config=config_to_use)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе: {str(e)}")

    missing_count = 0
    duplicates_count = 0
    mapped_issues = []

    for raw_issue in raw_result["issues"]:
        mapped_issues.append(Issue(
            type=raw_issue["type"],
            column=raw_issue.get("column"),
            description=raw_issue.get("message", "Описание отсутствует"),
            count=raw_issue["count"],
            recommendation="Рекомендуется проверить эти строки"
        ))

        if raw_issue["type"] == "missing":
            missing_count += raw_issue["count"]
        elif raw_issue["type"] in ["duplicate_row", "duplicate_key"]:
            duplicates_count += raw_issue["count"]

    profile = DataProfile(
        file_name=dataset["file_name"],
        file_type=dataset["file_type"],
        rows_count=raw_result["total_rows"],
        columns_count=len(raw_result["columns"]),
        columns=raw_result["columns"],
        missing_values=missing_count,
        duplicates=duplicates_count
    )

    report = Report(
        report_id=str(uuid.uuid4()),
        status="completed",
        profile=profile,
        issues=mapped_issues,
        total_issues=len(mapped_issues),
        recommendations=["Исправьте найденные ошибки для повышения качества данных."]
    )
    
    save_report(report.report_id, report.model_dump()) 
    return report