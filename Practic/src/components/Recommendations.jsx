import "./Recommendations.css";
import { CATEGORIES, CATEGORY_ORDER, countByCategory } from "../utils/issueCategories";

function Recommendations({ issues = [] }) {
  // Сколько ошибок в каждой группе (пропуски, дубли, некорректные, несогласованности)
  const counts = countByCategory(issues);

  const recommendations = CATEGORY_ORDER
    .filter((category) => counts[category] > 0)
    .map((category) => ({ category, ...CATEGORIES[category] }));

  return (
    <section className="recommendations-section">
      <h2 className="recommendations-title"> Рекомендации по исправлению </h2>

      {recommendations.length === 0 ? (
      //если нет ошибок
        <div className="recommendation-success">
          <div className="success-icon">✓</div>

          <div>
            <h3>Ошибки не обнаружены</h3>
            <p> Данные успешно прошли проверку, исправления не требуются!</p>
          </div>
        </div>
      ) : (
        <div className="recommendations-list">
        {/* если есть ошибки */}
          {recommendations.map((item) => (
            <div className="recommendation-card" key={item.category} >
              <div
                className="recommendation-indicator"
                style={{ backgroundColor: item.color }}
              />

              <div className="recommendation-content">
                <div className="recommendation-header">
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
