import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { formatDate } from "../utils/formatDate";
import "./ReportPage.css";

function ReportPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Берём историю с бэкенда, свежие отчёты приходят первыми
    fetch("/api/history")
      .then(res => res.json())
      .then(data => {
        setReports(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Ошибка загрузки истории:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="page" style={{ padding: "40px", color: "white" }}>
      <h1 className="page-title">Отчёт по анализу</h1>
      <p className="page-subtitle">Список проверенных объектов. Нажмите на отчёт, чтобы открыть его</p>

      {loading ? (
        <div style={{ textAlign: "center", color: "#ACACAC", marginTop: "50px" }}>
          Загрузка истории...
        </div>
      ) : reports.length === 0 ? (
        <div style={{ textAlign: "center", color: "#ACACAC", marginTop: "50px" }}>
          Необходимые данные не найдены.<br/>
          <span style={{ fontSize: "14px", marginTop: "10px", display: "block" }}>
            Загрузите файл на главной странице, чтобы создать первый отчет.
          </span>
        </div>
      ) : (
        <div style={{ marginTop: "30px", display: "flex", flexDirection: "column", gap: "15px" }}>
          {reports.map((rep) => (
            <Link key={rep.report_id} to={`/reports/${rep.report_id}`} className="report-card">
              <div>
                <h3 style={{ margin: "0 0 10px 0", fontSize: "20px" }}>{rep.profile.file_name}</h3>
                <p style={{ margin: 0, color: "#ACACAC" }}>
                  Строк: {rep.profile.rows_count.toLocaleString()} |
                  Ошибок: <span style={{ color: "#ff4c4c", fontWeight: "bold" }}>{rep.total_issues}</span> |
                  Пропуски: {rep.profile.missing_values.toLocaleString()} |
                  Дубликаты: {rep.profile.duplicates.toLocaleString()} |
                  Некорректные: {(rep.profile.invalid_values || 0).toLocaleString()} |
                  Несогласованности: {(rep.profile.inconsistencies || 0).toLocaleString()}
                </p>
              </div>
              <div className="report-card-side">
                {rep.created_at && <span className="report-card-date">{formatDate(rep.created_at)}</span>}
                <span className="report-card-open">Открыть →</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default ReportPage;
