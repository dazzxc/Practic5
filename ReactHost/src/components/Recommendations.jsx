import styles from "./Recommendations.module.css";
import { CATEGORIES, CATEGORY_ORDER, countByCategory } from "../utils/issueCategories";

function Recommendations({ issues = [] }) {
  // только группы с ошибками
  const counts = countByCategory(issues);

  const recommendations = CATEGORY_ORDER
    .filter((category) => counts[category] > 0)
    .map((category) => ({ category, ...CATEGORIES[category] }));

  return (
    <section className={styles.recommendationsSection}>
      <h2 className={styles.recommendationsTitle}>Рекомендации по исправлению</h2>
      {recommendations.length === 0 ? (
        <div className={styles.recommendationSuccess}>
          <div className={styles.successIcon}>✓</div>
          <div>
            <h3>Ошибки не обнаружены</h3>
            <p>Данные успешно прошли проверку, исправления не требуются!</p>
          </div>
        </div>
      ) : (
        <div className={styles.recommendationsList}>
          {recommendations.map((item) => (
            <div className={styles.recommendationCard} key={item.category}>
              <div className={`${styles.recommendationIndicator} ${styles[item.category]}`} />
              <div className={styles.recommendationContent}>
                <div className={styles.recommendationHeader}>
                  <h3>{item.title}</h3>
                </div>
                <p>{item.text}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default Recommendations;
