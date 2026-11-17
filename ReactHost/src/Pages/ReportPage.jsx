import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { formatDate } from "../utils/formatDate";
import pageStyles from "./Page.module.css";
import styles from "./ReportPage.module.css";

function ReportPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // история, свежие первыми
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
    <div className={pageStyles.page}>
      <h1 className={pageStyles.pageTitle}>Отчёт по анализу</h1>
      <p className={pageStyles.pageSubtitle}>Список проверенных объектов. Нажмите на отчёт, чтобы открыть его</p>

      {loading ? (
        <div className={styles.message}>
          Загрузка истории...
        </div>
      ) : reports.length === 0 ? (
        <div className={styles.message}>
          Необходимые данные не найдены.
          <span className={styles.messageHint}>
            Загрузите файл на главной странице, чтобы создать первый отчет.
          </span>
        </div>
      ) : (
        <div className={styles.reportList}>
          {reports.map((rep) => (
            <Link key={rep.report_id} to={`/reports/${rep.report_id}`} className={styles.reportCard}>
              <div>
                <h3 className={styles.reportCardTitle}>{rep.profile.file_name}</h3>
                <p className={styles.reportCardStats}>
                  Строк: {rep.profile.rows_count.toLocaleString()} |
                  Ошибок: <span className={styles.reportCardErrors}>{rep.total_issues}</span> |
                  Пропуски: {rep.profile.missing_values.toLocaleString()} |
                  Дубликаты: {rep.profile.duplicates.toLocaleString()} |
                  Некорректные: {(rep.profile.invalid_values || 0).toLocaleString()} |
                  Несогласованности: {(rep.profile.inconsistencies || 0).toLocaleString()}
                </p>
              </div>
              <div className={styles.reportCardSide}>
                {rep.created_at && <span className={styles.reportCardDate}>{formatDate(rep.created_at)}</span>}
                <span className={styles.reportCardOpen}>Открыть →</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default ReportPage;
