import { useState, useRef, useEffect } from "react";
import "./MainPage.css";

function MainPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  
  // Инициализируем отчет из localStorage, чтобы он не пропадал
  const [report, setReport] = useState(() => {
    const saved = localStorage.getItem("lastReport");
    return saved ? JSON.parse(saved) : null;
  });
  
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setReport(null);
      localStorage.removeItem("lastReport"); // Очищаем старый отчет при выборе нового файла
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Пожалуйста, выберите файл для анализа.");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      setStatusText("Загрузка файла на сервер...");
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) throw new Error("Ошибка при загрузке файла");
      const uploadData = await uploadRes.json();

      setStatusText("Анализ данных...");
      const analyzeRes = await fetch("/api/run-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: uploadData.dataset_id }),
      });

      if (!analyzeRes.ok) throw new Error("Ошибка при анализе данных");
      const reportData = await analyzeRes.json();

      setReport(reportData);
      localStorage.setItem("lastReport", JSON.stringify(reportData)); // Сохраняем в localStorage
      setStatusText("");
    } catch (err) {
      setError(err.message || "Произошла ошибка");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!report) return;
    
    try {
      const res = await fetch(`/api/export/${format}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(report),
      });

      if (!res.ok) throw new Error("Ошибка при генерации файла");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = format === "excel" ? "data_quality_report.xlsx" : "data_quality_report.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="page">
      <h1 className="page-title">Анализ качества данных</h1>
      <p className="page-subtitle"> Загрузите CSV, Excel или JSON файл, чтобы проверить его качество </p>

      <div className="upload-card">
        <div className="upload-area">
          <input 
            type="file" 
            accept=".csv, .json, .xlsx" 
            onChange={handleFileChange} 
            ref={fileInputRef}
            style={{ display: "none" }} 
          />
          
          <div style={{ fontSize: "40px", marginBottom: "10px" }}>📁</div>

          <h2 className="text-title">
            {file ? file.name : "Перетащите файл сюда"}
          </h2>

          <p className="text-subtitle">
            Или <span className="text-blue" onClick={() => fileInputRef.current.click()} style={{ cursor: "pointer", textDecoration: "underline" }}>выберите файл</span> на компьютере
          </p>
        </div>

        <button 
          className="primary-button" 
          onClick={file ? handleAnalyze : () => fileInputRef.current.click()}
          disabled={loading}
        >
          {loading ? statusText : (file ? "Запустить аудит" : "Выбрать файл")}
        </button>
        {error && <p style={{ color: "#ff4c4c", marginTop: "15px" }}>{error}</p>}
      </div>

      {report && (
        <div className="report-dashboard" style={{ marginTop: "40px", animation: "fadeIn 0.5s ease-in-out" }}>
          
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h2>Отчет готов!</h2>
            
            <div style={{ display: "flex", gap: "10px" }}>
              <button 
                onClick={() => handleExport("json")}
                style={{ background: "#3734C7", color: "white", border: "none", padding: "10px 20px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}
              >
                Скачать JSON
              </button>
              <button 
                onClick={() => handleExport("excel")}
                style={{ background: "#217346", color: "white", border: "none", padding: "10px 20px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}
              >
                Скачать Excel
              </button>
            </div>
          </div>

          <div className="kpi-grid">
            <div className="kpi-card">
              <span className="kpi-title">Всего строк</span>
              <span className="kpi-value">{report.profile.rows_count.toLocaleString()}</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-title">Пропуски</span>
              <span className="kpi-value danger">{report.profile.missing_values.toLocaleString()}</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-title">Дубликаты</span>
              <span className="kpi-value warning">{report.profile.duplicates.toLocaleString()}</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-title">Типов ошибок</span>
              <span className="kpi-value info">{report.total_issues}</span>
            </div>
          </div>

          <h3>Найденные проблемы</h3>
          <table className="issues-table">
            <thead>
              <tr>
                <th>Тип</th>
                <th>Колонка</th>
                <th>Описание</th>
                <th>Количество</th>
              </tr>
            </thead>
            <tbody>
              {report.issues.map((issue, index) => (
                <tr key={index}>
                  <td><span className="badge">{issue.type}</span></td>
                  <td>{issue.column || "Вся строка"}</td>
                  <td>{issue.description}</td>
                  <td className="count-cell">{issue.count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default MainPage;