import { useState, useRef, useEffect } from "react";
import pageStyles from "./Page.module.css";
import styles from "./MainPage.module.css";
import ReportView from "../components/ReportView";
import CheckSettings from "../components/CheckSettings";
import { CATEGORY_ORDER } from "../utils/issueCategories";

const SCROLL_DURATION = 1200; // длительность прокрутки, мс
const SCROLL_OFFSET = 40;     // отступ над отчётом

// ищем скролл-контейнер
function getScrollContainer(element) {
  let parent = element.parentElement;
  while (parent) {
    const overflowY = getComputedStyle(parent).overflowY;
    if ((overflowY === "auto" || overflowY === "scroll") && parent.scrollHeight > parent.clientHeight) {
      return parent;
    }
    parent = parent.parentElement;
  }
  return document.scrollingElement || document.documentElement;
}

// плавный разгон и торможение
function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// прокрутка к блоку
function smoothScrollTo(element) {
  const container = getScrollContainer(element);
  const isPage = container === document.scrollingElement || container === document.documentElement;
  const containerTop = isPage ? 0 : container.getBoundingClientRect().top;

  const start = container.scrollTop;
  const target = start + element.getBoundingClientRect().top - containerTop - SCROLL_OFFSET;
  const distance = target - start;
  const startTime = performance.now();

  function step(now) {
    const progress = Math.min((now - startTime) / SCROLL_DURATION, 1);
    container.scrollTop = start + distance * easeInOutCubic(progress);
    if (progress < 1) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}

function MainPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  // счётчик, чтобы рамка не мигала
  const dragCounter = useRef(0);

  // настройки проверки
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [groups, setGroups] = useState(CATEGORY_ORDER);
  const [ruleMode, setRuleMode] = useState("auto");
  const [rules, setRules] = useState(null);
  const [autoRules, setAutoRules] = useState(null);
  const [columns, setColumns] = useState([]);
  const [dateFormats, setDateFormats] = useState([]);
  const [rulesLoading, setRulesLoading] = useState(false);
  // файл уже на сервере: { file, id }
  const uploadedRef = useRef(null);

  const fileInputRef = useRef(null);
  const reportRef = useRef(null); // цель прокрутки

  // листаем к отчёту
  useEffect(() => {
    if (report && reportRef.current) {
      // ждём отрисовку
      const timer = setTimeout(() => smoothScrollTo(reportRef.current), 200);
      return () => clearTimeout(timer);
    }
  }, [report]);

  // новый файл - правила старого не подходят
  const selectFile = (newFile) => {
    setFile(newFile);
    setError("");
    setReport(null);
    setRules(null);
    setAutoRules(null);
    setRuleMode("auto");
    uploadedRef.current = null;
  };

  const uploadFile = async () => {
    if (uploadedRef.current?.file === file) return uploadedRef.current.id;

    const formData = new FormData();
    formData.append("file", file);
    const uploadRes = await fetch("/api/upload", { method: "POST", body: formData });
    if (!uploadRes.ok) throw new Error("Ошибка при загрузке файла");
    const uploadData = await uploadRes.json();

    uploadedRef.current = { file, id: uploadData.dataset_id };
    return uploadData.dataset_id;
  };

  const loadRules = async () => {
    setRulesLoading(true);
    setError("");
    try {
      const datasetId = await uploadFile();
      const res = await fetch("/api/suggest-rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: datasetId }),
      });
      if (!res.ok) throw new Error("Не удалось прочитать колонки файла");
      const data = await res.json();
      setRules(data.rules);
      setAutoRules(data.rules);
      setColumns(data.columns);
      setDateFormats(data.date_formats);
    } catch (err) {
      setError(err.message || "Произошла ошибка");
      setRuleMode("auto");
    } finally {
      setRulesLoading(false);
    }
  };

  const handleModeChange = (mode) => {
    setRuleMode(mode);
    if (mode === "manual" && !rules) loadRules();
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      selectFile(e.target.files[0]);
    }
  };

  // drag-and-drop
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current += 1;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "copy";
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files && e.dataTransfer.files[0];
    if (droppedFile) {
      selectFile(droppedFile);
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
      const datasetId = await uploadFile();

      setStatusText("Анализ данных...");
      const analyzeRes = await fetch("/api/run-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_id: datasetId,
          // null - все группы и автоподбор
          groups: groups.length === CATEGORY_ORDER.length ? null : groups,
          config: ruleMode === "manual" && rules ? rules : null,
        }),
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
    <section className={pageStyles.page}>
      <h1 className={pageStyles.pageTitle}>Анализ качества данных</h1>
      <p className={pageStyles.pageSubtitle}>Загрузите CSV, Excel или JSON файл, чтобы проверить его качество</p>
      <div
        className={`${styles.uploadCard} ${isDragging ? styles.uploadCardDragging : ""}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className={styles.uploadArea}>
          <input 
            type="file" 
            accept=".csv, .json, .xlsx" 
            onChange={handleFileChange} 
            ref={fileInputRef}
            className={styles.hiddenInput}
          />
          <div className={styles.uploadIcon}>
            <svg width="132" height="132" viewBox="0 0 132 132" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M126.894 86.2629V113.35C126.894 116.943 125.467 120.387 122.927 122.927C120.387 125.467 116.943 126.894 113.35 126.894H18.5438C14.9518 126.894 11.5068 125.467 8.96689 122.927C6.42693 120.387 5 116.943 5 113.35V86.2629M99.8067 52.4033L65.9471 86.2629L32.0876 52.4033M65.9471 86.2629V5" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" stroke="currentColor"/>
            </svg>
          </div>
          <h2 className={styles.textTitle}>
            {file ? file.name : (isDragging ? "Отпустите файл здесь" : "Перетащите файл сюда")}
          </h2>
          <p className={styles.textSubtitle}>
            {/* подсказка про перетаскивание */}
            {file ? "Перетащите другой файл или " : "Или "}
            <span className={styles.fileLink} onClick={() => fileInputRef.current.click()}>
              {file ? "выберите его" : "выберите файл"}
            </span> на компьютере
          </p>
        </div>
        <button 
          className={styles.primaryButton} 
          onClick={file ? handleAnalyze : () => fileInputRef.current.click()}
          disabled={loading || rulesLoading || (file && groups.length === 0)}
        >
          {loading ? (
            <>
              {statusText.replace(/\.+$/, "")}
              <span className={styles.dots}>
                <span>.</span><span>.</span><span>.</span>
              </span>
            </>
          ) : (file ? "Запустить аудит" : "Выбрать файл")}
        </button>
        {error && <p className={styles.errorText}>{error}</p>}
      </div>
      {file && (
        <div className={styles.settingsCard}>
          <button
            type="button"
            className={styles.settingsToggle}
            onClick={() => setSettingsOpen(!settingsOpen)}
          >
            Настройки проверки
            <span className={settingsOpen ? styles.arrowOpen : styles.arrow}>▾</span>
          </button>
          {settingsOpen && (
            <CheckSettings
              groups={groups}
              onGroupsChange={setGroups}
              mode={ruleMode}
              onModeChange={handleModeChange}
              rules={rules}
              onRulesChange={setRules}
              columns={columns}
              dateFormats={dateFormats}
              rulesLoading={rulesLoading}
              onReset={() => setRules(autoRules)}
            />
          )}
        </div>
      )}
      {/* результат */}
      {report && (
        <div
          className={`${pageStyles.reportDashboard} ${styles.reportBlock}`}
          ref={reportRef}
        >
          <h2>Отчет готов!</h2>
          <ReportView report={report} />
        </div>
      )}
    </section>
  );
}

export default MainPage;
