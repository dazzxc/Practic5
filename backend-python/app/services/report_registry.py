# отчёты в памяти, после перезапуска пропадут
reports_db = {}


def save_report(report_id: str, report_data: dict):
    reports_db[report_id] = report_data


def get_all_reports():
    # свежие сверху
    return sorted(reports_db.values(), key=lambda r: r.get("created_at") or "", reverse=True)


def get_report(report_id: str):
    return reports_db.get(report_id)
