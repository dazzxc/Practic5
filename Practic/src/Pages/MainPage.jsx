import { useState, useRef } from "react";
import "./MainPage.css"; // Обрати внимание: у него путь ../ (на уровень выше), это нормально
import DataDistribution from "../components/DataDistribution";
import Recommendations from "../components/Recommendations";

function MainPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  
  // Скрытый инпут для выбора файла через кнопку
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setReport(null);
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
      setStatusText("");
    } catch (err) {
      setError(err.message || "Произошла ошибка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page">
      <h1 className="page-title">Анализ качества данных</h1>
      <p className="page-subtitle"> Загрузите CSV, Excel или JSON файл, чтобы проверить его качество </p>

      <div className="upload-card">
        <div className="upload-area">
          {/* Скрытый инпут для файла */}
          <input 
            type="file" 
            accept=".csv, .json, .xlsx" 
            onChange={handleFileChange} 
            ref={fileInputRef}
            style={{ display: "none" }} 
          />
          
          {/* Иконка (пока текстом, как в его коде, потом можно вставить SVG) */}
          <div ><svg width="132" height="132" viewBox="0 0 132 132" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M126.894 86.2629V113.35C126.894 116.943 125.467 120.387 122.927 122.927C120.387 125.467 116.943 126.894 113.35 126.894H18.5438C14.9518 126.894 11.5068 125.467 8.96689 122.927C6.42693 120.387 5 116.943 5 113.35V86.2629M99.8067 52.4033L65.9471 86.2629L32.0876 52.4033M65.9471 86.2629V5" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke="#3734C7"/>
</svg>
</div>

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

      {/* Наш блок с результатами (появляется после анализа) */}
      {report && (
        <div className="report-dashboard" style={{ marginTop: "40px", animation: "fadeIn 0.5s ease-in-out" }}>
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
          
          <div>
            <DataDistribution report={report} />
            {/* график  */}
          </div>

          <div>
            <Recommendations issues={report?.issues} />
            {/* Рекомендации по исправлению ошибок */}
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