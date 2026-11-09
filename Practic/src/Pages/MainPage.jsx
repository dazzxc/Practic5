import { useState } from "react";
import "./MainPage.css";

function MainPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  // Обработчик выбора файла
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setReport(null);
    }
  };

  // Обработчик запуска
  const handleAnalyze = async () => {
    if (!file) {
      setError("Пожалуйста, выберите файл для анализа.");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      // 1. Загружаем файл
      setStatusText("Загрузка файла на сервер...");
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) throw new Error("Ошибка при загрузке файла");
      const uploadData = await uploadRes.json();

      // 2. Запускаем проверку
      setStatusText("Анализ данных (может занять время)...");
      const analyzeRes = await fetch("/api/run-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: uploadData.dataset_id }),
      });

      if (!analyzeRes.ok) throw new Error("Ошибка при анализе данных");
      const reportData = await analyzeRes.json();

      // 3. Сохраняем результат
      setReport(reportData);
      setStatusText("");
    } catch (err) {
      setError(err.message || "Произошла ошибка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-page">
      <h1>Аудит качества данных</h1>
      
      {/* Блок загрузки */}
      <div className="upload-card">
        <input 
          type="file" 
          accept=".csv, .json, .xlsx" 
          onChange={handleFileChange} 
          id="file-upload" 
          className="file-input"
        />
        <label htmlFor="file-upload" className="file-label">
          {file ? file.name : "Нажмите, чтобы выбрать файл (CSV, JSON, XLSX)"}
        </label>
        
        <button 
          className="analyze-btn" 
          onClick={handleAnalyze} 
          disabled={loading || !file}
        >
          {loading ? statusText : "Запустить аудит"}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {/* Блок результатов */}
      {report && (
        <div className="report-dashboard">
          <h2>Отчет готов!</h2>
          
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
    </div>
  );
}

export default MainPage;