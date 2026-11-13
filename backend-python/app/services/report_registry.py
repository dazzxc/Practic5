# Простое хранилище в оперативной памяти (как предложил твой коллега)
reports_db = {}

def save_report(report_id: str, report_data: dict):
    reports_db[report_id] = report_data

def get_all_reports():
    return list(reports_db.values())

def get_report(report_id: str):
    return reports_db.get(report_id)