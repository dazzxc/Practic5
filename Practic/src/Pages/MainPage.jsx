import { useState, useRef } from "react";
import "./MainPage.css";

function MainPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [report, setReport] = useState(() => {
    const saved = localStorage.getItem("lastReport");
    return saved ? JSON.parse(saved) : null;
  });
  const [error, setError] = useState("");
  
  const fileInputRef = useRef(null);

  // --- СОСТОЯНИЯ ДЛЯ НАСТРОЕК ПРАВИЛ ---
  const [rules, setRules] = useState({
    missing: true,
    duplicates: true,
    duplicateKey: "id",
    email: true,
    ageMin: 0,
    ageMax: 120,
    dates: true,
  });

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setReport(null);
      localStorage.removeItem("lastReport");
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

      // Формируем конфиг на основе выбора пользователя
      const userConfig = {
        key_columns: rules.duplicates ? [rules.duplicateKey] : [],
        invalid_rules: {
          ...(rules.email ? { "email": { "type": "email" } } : {}),
          ...(rules.ageMin !== "" && rules.ageMax !== "" 
            ? { "age": { "type": "number", "min": Number(rules.ageMin), "max": Number(rules.ageMax) } } 
            : {})
        },
        consistency_rules: rules.dates ? [
          { "rule": "dates_order", "start": "start_date", "end": "end_date", "format": "%d.%m.%Y" }
        ] : []
      };

      setStatusText("Анализ данных...");
      const analyzeRes = await fetch("/api/run-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          dataset_id: uploadData.dataset_id,
          config: userConfig 
        }),
      });

      if (!analyzeRes.ok) throw new Error("Ошибка при анализе данных");
      const reportData = await analyzeRes.json();

      setReport(reportData);
      localStorage.setItem("lastReport", JSON.stringify(reportData));
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

      {/* БЛОК НАСТРОЕК ПРАВИЛ */}
      {file && !loading && (
        <div style={{ marginTop: "30px", background: "#161826", padding: "25px", borderRadius: "12px" }}>
          <h3 style={{ marginTop: 0, color: "white", marginBottom: "20px" }}>Настройки проверок</h3>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", color: "white" }}>
            
            <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
              <input type="checkbox" checked={rules.missing} onChange={(e) => setRules({...rules, missing: e.target.checked})} />
              Искать пропуски
            </label>

            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <input type="checkbox" checked={rules.duplicates} onChange={(e) => setRules({...rules, duplicates: e.target.checked})} />
              <span>Дубликаты по:</span>
              <input 
                type="text" 
                value={rules.duplicateKey} 
                onChange={(e) => setRules({...rules, duplicateKey: e.target.value})}
                disabled={!rules.duplicates}
                style={{ background: "#25246a", border: "none", color: "white", padding: "5px", borderRadius: "4px", width: "80px" }}
              />
            </div>

            <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
              <input type="checkbox" checked={rules.email} onChange={(e) => setRules({...rules, email: e.target.checked})} />
              Проверять формат Email
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
              <input type="checkbox" checked={rules.dates} onChange={(e) => setRules({...rules, dates: e.target.checked})} />
              Проверять порядок дат
            </label>

            <div style={{ display: "flex", alignItems: "center", gap: "10px", gridColumn: "span 2" }}>
              <span>Возраст в диапазоне:</span>
              <input 
                type="number" 
                value={rules.ageMin} 
                onChange={(e) => setRules({...rules, ageMin: e.target.value})}
                style={{ background: "#25246a", border: "none", color: "white", padding: "5px", borderRadius: "4px", width: "80px" }}
              />
              <span>—</span>
              <input 
                type="number" 
                value={rules.ageMax} 
                onChange={(e) => setRules({...rules, ageMax: e.target.value})}
                style={{ background: "#25246a", border: "none", color: "white", padding: "5px", borderRadius: "4px", width: "80px" }}
              />
            </div>

          </div>
        </div>
      )}

      {report && (
        <div className="report-dashboard" style={{ marginTop: "40px", animation: "fadeIn 0.5s ease-in-out" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h2>Отчет готов!</h2>
            <div style={{ display: "flex", gap: "10px" }}>
              <button onClick={() => handleExport("json")} style={{ background: "#3734C7", color: "white", border: "none", padding: "10px 20px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>Скачать JSON</button>
              <button onClick={() => handleExport("excel")} style={{ background: "#217346", color: "white", border: "none", padding: "10px 20px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>Скачать Excel</button>
            </div>
          </div>

          <div className="kpi-grid">
            <div className="kpi-card"><span className="kpi-title">Всего строк</span><span className="kpi-value">{report.profile.rows_count.toLocaleString()}</span></div>
            <div className="kpi-card"><span className="kpi-title">Пропуски</span><span className="kpi-value danger">{report.profile.missing_values.toLocaleString()}</span></div>
            <div className="kpi-card"><span className="kpi-title">Дубликаты</span><span className="kpi-value warning">{report.profile.duplicates.toLocaleString()}</span></div>
            <div className="kpi-card"><span className="kpi-title">Типов ошибок</span><span className="kpi-value info">{report.total_issues}</span></div>
          </div>

          <h3>Найденные проблемы</h3>
          <table className="issues-table">
            <thead><tr><th>Тип</th><th>Колонка</th><th>Описание</th><th>Количество</th></tr></thead>
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