import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ReportView from "../components/ReportView";
import { formatDate } from "../utils/formatDate";
import "./ReportPage.css";

// Страница одного прошлого отчёта: /reports/<id>
function ReportDetailPage() {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    fetch(`/api/get-report/${reportId}`)
      .then((res) => {
        if (res.status === 404) throw new Error("Отчёт не найден. Возможно, сервер перезапускался.");
        if (!res.ok) throw new Error("Не удалось загрузить отчёт");
        return res.json();
      })
      .then((data) => setReport(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [reportId]);

  return (
    <section className="page" style={{ padding: "40px", color: "white" }}>
      <Link to="/reports" className="back-link">← Ко всем отчётам</Link>

      {loading && <div className="report-message">Загрузка отчёта...</div>}

      {error && <div className="report-message">{error}</div>}

      {report && (
        <div className="report-dashboard" style={{ animation: "fadeIn 0.4s ease-in-out" }}>
          <h1 className="page-title">{report.profile.file_name}</h1>
          <p className="page-subtitle">
            {report.created_at ? `Проверен ${formatDate(report.created_at)}` : "Сохранённый отчёт"}
            {report.auto_rules ? " · правила подобраны автоматически" : ""}
          </p>

          <ReportView report={report} />
        </div>
      )}
    </section>
  );
}

export default ReportDetailPage;
