
import "./DataDistribution.css";

const ERROR_TYPES = [
  {
    type: "missing",
    label: "Пропуски",
    color: "#D7DF55",
  },
  {
    type: "duplicate_row",
    label: "Дубликаты",
    color: "#169BD5",
  },
  {
    type: "invalid_value",
    label: "Некорректные значения",
    color: "#D9444A",
  },
  {
    type: "inconsistency",
    label: "Несогласованности",
    color: "#E17A21",
  },
];

const CORRECT_COLOR = "#54B65F";

function DataDistribution({ report }) {
  const issues = report?.issues || [];
  const profile = report?.profile;

  const totalCells =
    (profile?.rows_count || 0) *
    (profile?.columns_count || 0);

  const missingValues = profile?.missing_values || 0;

  // Предварительный процент заполненных ячеек.
  const correctPercentage =
    totalCells > 0
      ? Math.max(
          0,
          Math.min(
            100,
            ((totalCells - missingValues) / totalCells) * 100
          )
        )
      : 0;

  // Группируем ошибки по типам.
  const groupedIssues = issues.reduce((result, issue) => {
    const type = issue.type;
    const count = Number(issue.count) || 0;

    if (!result[type]) {
      const errorType = ERROR_TYPES.find(
        (item) => item.type === type
      );

      result[type] = {
        type,
        label: errorType?.label || type,
        color: errorType?.color || "#A29AC3",
        count: 0,
      };
    }

    result[type].count += count;

    return result;
  }, {});

  const distribution = Object.values(groupedIssues).filter(
    (item) => item.count > 0
  );

  const totalErrors = distribution.reduce(
    (sum, item) => sum + item.count,
    0
  );

  // Строим диаграмму: зелёный сектор — заполненные ячейки,
  // остальные сектора — доли найденных ошибок.
  const errorPercentage = 100 - correctPercentage;

  let currentAngle = correctPercentage * 3.6;

  const gradientParts = [];

  if (correctPercentage > 0) {
    gradientParts.push(
      `${CORRECT_COLOR} 0deg ${currentAngle}deg`
    );
  }

  distribution.forEach((item) => {
    const percentage =
      totalErrors > 0
        ? (item.count / totalErrors) * errorPercentage
        : 0;

    const startAngle = currentAngle;
    currentAngle += percentage * 3.6;

    if (percentage > 0) {
      gradientParts.push(
        `${item.color} ${startAngle}deg ${currentAngle}deg`
      );
    }
  });

  const gradient =
    totalCells > 0
      ? `conic-gradient(${gradientParts.join(", ")})`
      : "conic-gradient(#292B3B 0deg 360deg)";

  return (
    <section className="distribution-section">
      <div className="distribution-card">
        <h2 className="distribution-title">
          Распределение проблем
        </h2>

        <div className="distribution-content">
          <div
            className="donut-chart"
            style={{ background: gradient }}
          >
            <div className="donut-center">
              <span className="donut-total">
                {correctPercentage.toFixed(1)}%
              </span>

              <span className="donut-label">
                корректных данных
              </span>
            </div>
          </div>

          <div className="distribution-legend">
            <div className="legend-item">
              <span
                className="legend-color"
                style={{ backgroundColor: CORRECT_COLOR }}
              />

              <span className="legend-label">
                Корректные данные
              </span>

              <span className="legend-value">
                {correctPercentage.toFixed(1)}%
              </span>
            </div>

            {distribution.map((item) => {
              const percentage =
                totalErrors > 0
                  ? (item.count / totalErrors) * errorPercentage
                  : 0;

              return (
                <div
                  className="legend-item"
                  key={item.type}
                >
                  <span
                    className="legend-color"
                    style={{ backgroundColor: item.color }}
                  />

                  <span className="legend-label">
                    {item.label}
                  </span>

                  <span className="legend-value">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="error-types-card">
        <h2 className="distribution-title">
          Типы ошибок
        </h2>

        <div className="error-types-list">
          {ERROR_TYPES.map((item) => (
            <div
              className="error-type-item"
              key={item.type}
            >
              <span
                className="legend-color"
                style={{ backgroundColor: item.color }}
              />

              <span className="error-type-label">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default DataDistribution;
