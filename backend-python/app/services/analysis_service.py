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
from app.services.cache_service import (
    get_file_hash,
    make_cache_key,
    get_cached_report,
    save_cached_report
)

# путь к движку проверок
current_dir = Path(__file__).resolve().parent
qa_checks_path = current_dir.parents[2] / "qa_checks" / "CHECKS"

if not (qa_checks_path / "checks" / "__init__.py").exists():
    raise RuntimeError(f"Не нашёл движок проверок в папке {qa_checks_path}. Если папку переименовали, поправь путь здесь.")

sys.path.insert(0, str(qa_checks_path))

try:
    from checks import check_file
    from checks.auto_rules import DATE_FORMATS, suggest_rules
    from checks.reader import read_in_chunks
except ImportError as e:
    raise RuntimeError(f"Не удалось импортировать check_file. Ошибка: {e}")


RECOMMENDATIONS = {
    "missing": "Заполните пустые ячейки корректными значениями или удалите неполные строки.",
    "duplicate": "Удалите повторяющиеся строки и проверьте уникальность ключевых полей (id).",
    "invalid": "Исправьте значения неверного типа, формата или вне допустимого диапазона.",
    "inconsistency": "Проверьте связанные поля: даты окончания и начала, суммы и их составляющие.",
}


def _get_file(dataset_id):
    dataset = get_dataset(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if not dataset["file_path"].exists():
        raise HTTPException(status_code=404, detail="Dataset file does not exist")
    return dataset


def suggest_file_rules(dataset_id: str) -> dict:
    dataset = _get_file(dataset_id)
    try:
        first_chunk = next(iter(read_in_chunks(str(dataset["file_path"]))), None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при чтении файла: {str(e)}")

    if first_chunk is None:
        return {"columns": [], "rules": {"key_columns": [], "invalid_rules": {}, "consistency_rules": []}, "date_formats": DATE_FORMATS}

    return {
        "columns": [str(c) for c in first_chunk.columns],
        "rules": suggest_rules(first_chunk),
        "date_formats": DATE_FORMATS,
    }



def run_data_analysis(request: AnalysisRequest) -> Report:
    dataset = _get_file(request.dataset_id)
    file_path = dataset["file_path"]

    # ========== КЭШИРОВАНИЕ ==========
    file_hash = get_file_hash(file_path)
    cache_key = make_cache_key(file_hash, request.config, request.groups)

    cached = get_cached_report(cache_key)
    if cached:
        # Берём из кэша, но всё равно добавляем в историю как новый отчёт
        report = Report(**cached)
        
        # Создаём новый ID и время, чтобы в истории это была отдельная запись
        report.report_id = str(uuid.uuid4())
        report.created_at = datetime.now().isoformat(timespec="seconds")
        
        save_report(report.report_id, report.model_dump())
        return report
    # ================================

    config_to_use = request.config if request.config else None

    try:
        raw_result = check_file(str(file_path), config=config_to_use)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе: {str(e)}")

    # Фильтрация по выбранным группам
    raw_issues = raw_result["issues"]
    if request.groups is not None:
        raw_issues = [i for i in raw_issues if i.get("category") in request.groups]

    mapped_issues = []
    for raw_issue in raw_issues:
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

    summary = {category: 0 for category in RECOMMENDATIONS}
    for issue in raw_issues:
        cat = issue.get("category", "invalid")
        summary[cat] = summary.get(cat, 0) + issue["count"]

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
        checked_groups=request.groups,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )

    report_dict = report.model_dump()

    # Сохраняем в кэш
    save_cached_report(cache_key, report_dict)

    # Сохраняем в обычную историю
    save_report(report.report_id, report_dict)

    return report