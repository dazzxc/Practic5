import json
import pandas as pd
from .schemas import QualityReport

class ReportGenerator:
    @staticmethod
    def save_json(report: QualityReport, filename: str = "dq_report.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=4, ensure_ascii=False)
        print(f"💾 JSON-отчет сохранен в {filename}")

    @staticmethod
    def save_excel(report: QualityReport, filename: str = "dq_report.xlsx"):
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            summary_data = {
                "Метрика": ["Дата проверки", "Всего строк", "Всего колонок", "Полнота (%)", "Индекс качества"],
                "Значение": [report.timestamp, report.total_rows, report.total_columns, f"{report.metrics['completeness_score']}%", report.metrics['quality_score']]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Сводка", index=False)
            
            issues_list = [{
                "Тип проверки": i.check_type, "Поле": i.column, "Критичность": i.severity, "Описание": i.message, "Кол-во": i.count
            } for i in report.issues]
            
            pd.DataFrame(issues_list if issues_list else [{"Статус": "Ошибок нет"}]).to_excel(writer, sheet_name="Ошибки", index=False)
        print(f"💾 Excel-отчет сохранен в {filename}")