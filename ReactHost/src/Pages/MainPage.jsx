import { useState, useRef, useEffect } from "react";
import pageStyles from "./Page.module.css";
import styles from "./MainPage.module.css";
import ReportView from "../components/ReportView";

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

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setReport(null);
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
      setFile(droppedFile);
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
          disabled={loading}
        >
          {loading ? statusText : (file ? "Запустить аудит" : "Выбрать файл")}
        </button>
        {error && <p className={styles.errorText}>{error}</p>}
      </div>
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
