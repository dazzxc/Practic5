from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
import json
import io
import pandas as pd

router = APIRouter()

@router.post("/export/json")
async def export_json(report_data: dict):
    """Отдает отчет в виде JSON файла."""
    try:
        json_str = json.dumps(report_data, ensure_ascii=False, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="data_quality_report.json"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/excel")
async def export_excel(report_data: dict):
    """Отдает отчет в виде красивого Excel файла."""
    try:
        # 1. Лист со сводкой (Профиль)
        profile = report_data.get("profile", {})
        summary_data = {
            "Метрика": ["Имя файла", "Всего строк", "Колонок", "Пропуски", "Дубликаты",
                        "Некорректные значения", "Несогласованности", "Типов ошибок"],
            "Значение": [
                profile.get("file_name", "N/A"),
                profile.get("rows_count", 0),
                profile.get("columns_count", 0),
                profile.get("missing_values", 0),
                profile.get("duplicates", 0),
                profile.get("invalid_values", 0),
                profile.get("inconsistencies", 0),
                report_data.get("total_issues", 0)
            ]
        }
        df_summary = pd.DataFrame(summary_data)

        # 2. Лист с ошибками
        issues = report_data.get("issues", [])
        if issues:
            df_issues = pd.DataFrame(issues)
            # Группа ошибки по-русски (в старых отчётах поля category может не быть)
            category_names = {
                "missing": "Пропуски",
                "duplicate": "Дубликаты",
                "invalid": "Некорректные значения",
                "inconsistency": "Несогласованности",
            }
            if "category" not in df_issues.columns:
                df_issues["category"] = ""
            df_issues["category"] = df_issues["category"].map(category_names).fillna("")
            # Переименуем колонки для красоты
            df_issues = df_issues.rename(columns={
                "category": "Группа",
                "type": "Тип ошибки",
                "column": "Колонка",
                "description": "Описание",
                "count": "Количество"
            })
            # Оставим только нужные колонки
            df_issues = df_issues[["Группа", "Тип ошибки", "Колонка", "Описание", "Количество"]]
        else:
            df_issues = pd.DataFrame({"Информация": ["Ошибок не найдено"]})

        # 3. Записываем всё в один Excel файл с двумя листами
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Сводка', index=False)
            df_issues.to_excel(writer, sheet_name='Ошибки', index=False)
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="data_quality_report.xlsx"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации Excel: {str(e)}")