import styles from "./ReportView.module.css";
import DataDistribution from "./DataDistribution";
import Recommendations from "./Recommendations";
import { CATEGORIES, TYPE_LABELS, getCategory } from "../utils/issueCategories";

// отчёт целиком
function ReportView({ report }) {
  return (
    <>
      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <span className={styles.kpiTitle}>Всего строк</span>
          <span className={styles.kpiValue}>{report.profile.rows_count.toLocaleString()}</span>
        </div>
        <div className={styles.kpiCard}>
          <span className={styles.kpiTitle}>Пропуски</span>
          <span className={`${styles.kpiValue} ${styles.missing}`}>{report.profile.missing_values.toLocaleString()}</span>
        </div>
        <div className={styles.kpiCard}>
          <span className={styles.kpiTitle}>Дубликаты</span>
          <span className={`${styles.kpiValue} ${styles.duplicate}`}>{report.profile.duplicates.toLocaleString()}</span>
        </div>
        <div className={styles.kpiCard}>
          <span className={styles.kpiTitle}>Некорректные значения</span>
          <span className={`${styles.kpiValue} ${styles.invalid}`}>
            {(report.profile.invalid_values || 0).toLocaleString()}
          </span>
        </div>
        <div className={styles.kpiCard}>
          <span className={styles.kpiTitle}>Несогласованности</span>
          <span className={`${styles.kpiValue} ${styles.inconsistency}`}>
            {(report.profile.inconsistencies || 0).toLocaleString()}
          </span>
        </div>
        <div className={styles.kpiCard}>
          <span className={styles.kpiTitle}>Типов ошибок</span>
          <span className={`${styles.kpiValue} ${styles.kpiValueInfo}`}>{report.total_issues}</span>
        </div>
      </div>
      <DataDistribution report={report} />
      <Recommendations issues={report.issues} />
      <h3 className={styles.issuesTitle}>Найденные проблемы</h3>
      <table className={styles.issuesTable}>
        <thead>
          <tr>
            <th>Группа</th>
            <th>Тип</th>
            <th>Колонка</th>
            <th>Описание</th>
            <th>Количество</th>
          </tr>
        </thead>
        <tbody>
          {report.issues.map((issue, index) => {
            const categoryKey = getCategory(issue);
            const category = CATEGORIES[categoryKey];
            return (
            <tr key={index}>
              <td>
                <span className={`${styles.badge} ${styles[categoryKey]}`}>
                  {category.label}
                </span>
              </td>
              <td>{TYPE_LABELS[issue.type] || issue.type}</td>
              <td>{issue.column || "Вся строка"}</td>
              <td>{issue.description}</td>
              <td className={styles.countCell}>{issue.count.toLocaleString()}</td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}

export default ReportView;
