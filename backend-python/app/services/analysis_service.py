import sys
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

from app.schemas.analysis import AnalysisRequest
from app.schemas.report import Report
from app.schemas.profile import DataProfile
from app.schemas.common import Issue
from app.services.dataset_registry import get_dataset
from app.services.report_registry import save_report

# Подключаем движок проверок из папки qa_checks
current_dir = Path(__file__).resolve().parent
qa_checks_path = current_dir.parents[2] / "qa_checks" / "qa_checks"
sys.path.append(str(qa_checks_path))

try:
    from checks import check_file
except ImportError as e:
    raise RuntimeError(f"Не удалось импортировать check_file. Ошибка: {e}")

# Совет для каждой группы ошибок
RECOMMENDATIONS = {
    "missing": "Заполните пустые ячейки корректными значениями или удалите неполные строки.",
    "duplicate": "Удалите повторяющиеся строки и проверьте уникальность ключевых полей (id).",
    "invalid": "Исправьте значения неверного типа, формата или вне допустимого диапазона.",
    "inconsistency": "Проверьте связанные поля: даты окончания и начала, суммы и их составляющие.",
}


def run_data_analysis(request: AnalysisRequest) -> Report:
    dataset = get_dataset(request.dataset_id)

    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset["file_path"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset file does not exist")

    # Нет своих правил - движок подберёт их сам под колонки файла
    config_to_use = request.config if request.config else None

    try:
        raw_result = check_file(str(file_path), config=config_to_use)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе: {str(e)}")

    mapped_issues = []
    for raw_issue in raw_result["issues"]:
        category = raw_issue.get("category", "invalid")
        mapped_issues.append(Issue(
            type=raw_issue["type"],
            category=category,
            column=raw_issue.get("column"),
            description=raw_issue.get("message", "Описание отсутствует"),
            count=raw_issue["count"],
            percent=raw_issue.get("percent", 0),
            severity=raw_issue.get("severity", "low"),
            sample_rows=[int(r) for r in raw_issue.get("sample_rows", [])],
            recommendation=RECOMMENDATIONS.get(category, "Рекомендуется проверить эти строки"),
        ))

    # Сколько ошибок в каждой группе
    summary = raw_result.get("summary", {})

    profile = DataProfile(
        file_name=dataset["file_name"],
        file_type=dataset["file_type"],
        rows_count=raw_result["total_rows"],
        columns_count=len(raw_result["columns"]),
        columns=[str(c) for c in raw_result["columns"]],
        missing_values=summary.get("missing", 0),
        duplicates=summary.get("duplicate", 0),
        invalid_values=summary.get("invalid", 0),
        inconsistencies=summary.get("inconsistency", 0),
    )

    # Советы только по тем группам, где что-то нашлось
    recommendations = [text for category, text in RECOMMENDATIONS.items() if summary.get(category)]
    if not recommendations:
        recommendations = ["Ошибок не найдено, данные в хорошем состоянии."]

    report = Report(
        report_id=str(uuid.uuid4()),
        status="completed",
        profile=profile,
        issues=mapped_issues,
        total_issues=len(mapped_issues),
        recommendations=recommendations,
        applied_rules=raw_result.get("config"),
        auto_rules=raw_result.get("auto_rules", False),
        created_at=datetime.now().isoformat(timespec="seconds"),
    )

    save_report(report.report_id, report.model_dump())
    return report
