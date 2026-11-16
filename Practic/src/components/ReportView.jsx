import "../Pages/MainPage.css";
import DataDistribution from "./DataDistribution";
import Recommendations from "./Recommendations";
import { CATEGORIES, TYPE_LABELS, getCategory } from "../utils/issueCategories";

// Сам отчёт: карточки, диаграмма, советы и таблица.
// Один и тот же на главной и на странице старого отчёта.
function ReportView({ report }) {
  return (
    <>
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
          <span className="kpi-title">Некорректные значения</span>
          <span className="kpi-value" style={{ color: CATEGORIES.invalid.color }}>
            {(report.profile.invalid_values || 0).toLocaleString()}
          </span>
        </div>
        <div className="kpi-card">
          <span className="kpi-title">Несогласованности</span>
          <span className="kpi-value" style={{ color: CATEGORIES.inconsistency.color }}>
            {(report.profile.inconsistencies || 0).toLocaleString()}
          </span>
        </div>
        <div className="kpi-card">
          <span className="kpi-title">Типов ошибок</span>
          <span className="kpi-value info">{report.total_issues}</span>
        </div>
      </div>

      <DataDistribution report={report} />

      <Recommendations issues={report.issues} />

      <h3>Найденные проблемы</h3>
      <table className="issues-table">
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
            const category = CATEGORIES[getCategory(issue)];
            return (
            <tr key={index}>
              <td>
                <span className="badge" style={{ borderLeft: `4px solid ${category.color}`, whiteSpace: "nowrap" }}>
                  {category.label}
                </span>
              </td>
              <td>{TYPE_LABELS[issue.type] || issue.type}</td>
              <td>{issue.column || "Вся строка"}</td>
              <td>{issue.description}</td>
              <td className="count-cell">{issue.count.toLocaleString()}</td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}

export default ReportView;
