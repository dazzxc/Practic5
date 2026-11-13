import { useState, useEffect } from "react";

function ReportPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Запрашиваем историю с бэкенда
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
      <p className="page-subtitle">Список проверенных объектов</p>

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
          {reports.map((rep, index) => (
            <div key={index} style={{ 
              background: "#161826", 
              padding: "20px", 
              borderRadius: "8px", 
              borderLeft: "4px solid #3734C7",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <div>
                <h3 style={{ margin: "0 0 10px 0", fontSize: "20px" }}>{rep.profile.file_name}</h3>
                <p style={{ margin: 0, color: "#ACACAC" }}>
                  Строк: {rep.profile.rows_count.toLocaleString()} | 
                  Ошибок: <span style={{ color: "#ff4c4c", fontWeight: "bold" }}>{rep.total_issues}</span> | 
                  Пропуски: {rep.profile.missing_values.toLocaleString()} | 
                  Дубликаты: {rep.profile.duplicates.toLocaleString()}
                </p>
              </div>
              <div style={{ color: "#555", fontSize: "12px", textAlign: "right" }}>
                ID: {rep.report_id.slice(0, 8)}...
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ReportPage;