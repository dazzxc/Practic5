import styles from "./DataDistribution.module.css";
import { CATEGORIES, CATEGORY_ORDER, countByCategory } from "../utils/issueCategories";

// группы ошибок
const ERROR_TYPES = CATEGORY_ORDER.map((category) => ({
  type: category,
  label: CATEGORIES[category].label,
  color: CATEGORIES[category].color,
}));

const CORRECT_COLOR = "var(--color-success)";
const EMPTY_COLOR = "var(--color-chart-empty)";
const DEGREES_PER_PERCENT = 360 / 100; // проценты в градусы

function DataDistribution({ report }) {
  const issues = report?.issues || [];
  const profile = report?.profile;

  const totalCells =
    (profile?.rows_count || 0) *
    (profile?.columns_count || 0);

  // ошибки по группам
  const counts = countByCategory(issues);

  // одна ошибка = одна ячейка
  const allErrors = Object.values(counts).reduce((sum, value) => sum + value, 0);

  // процент корректных
  const correctPercentage =
    totalCells > 0
      ? Math.max(
          0,
          Math.min(
            100,
            ((totalCells - allErrors) / totalCells) * 100
          )
        )
      : 0;

  // только непустые группы
  const distribution = ERROR_TYPES
    .map((item) => ({ ...item, count: counts[item.type] }))
    .filter((item) => item.count > 0);

  const totalErrors = distribution.reduce(
    (sum, item) => sum + item.count,
    0
  );

  const errorPercentage = 100 - correctPercentage;
  let currentAngle = correctPercentage * DEGREES_PER_PERCENT;
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
    currentAngle += percentage * DEGREES_PER_PERCENT;

    if (percentage > 0) {
      gradientParts.push(
        `${item.color} ${startAngle}deg ${currentAngle}deg`
      );
    }
  });

  const gradient =
    totalCells > 0
      ? `conic-gradient(${gradientParts.join(", ")})`
      : `conic-gradient(${EMPTY_COLOR} 0deg 360deg)`;

  return (
    <section className={styles.distributionSection}>
      <div className={styles.distributionCard}>
        <h2 className={styles.distributionTitle}>Распределение данных</h2>
        <div className={styles.distributionContent}>
          {/* цвет кольца зависит от данных */}
          <div
            className={styles.donutChart}
            style={{ background: gradient }}>
            <div className={styles.donutCenter}>
              <span className={styles.donutTotal}>
                {correctPercentage.toFixed(1)}%
              </span>
              <span className={styles.donutLabel}>
                корректных данных
              </span>
            </div>
          </div>
          <div className={styles.distributionLegend}>
            <div className={styles.legendItem}>
              <span className={`${styles.legendColor} ${styles.correct}`} />
              <span className={styles.legendLabel}>
                Корректные данные
              </span>
              <span className={styles.legendValue}>
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
                  className={styles.legendItem}
                  key={item.type}
                >
                  <span className={`${styles.legendColor} ${styles[item.type]}`} />
                  <span className={styles.legendLabel}>
                    {item.label}
                  </span>
                  <span className={styles.legendValue}>
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <div className={styles.errorTypesCard}>
        <h2 className={styles.distributionTitle}>
          Типы ошибок
        </h2>
        <div className={styles.errorTypesList}>
          {ERROR_TYPES.map((item) => (
            <div
              className={styles.errorTypeItem}
              key={item.type}
            >
              <span className={`${styles.legendColor} ${styles[item.type]}`} />
              <span className={styles.errorTypeLabel}>
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
