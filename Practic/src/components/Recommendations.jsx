import "./Recommendations.css";

const RECOMMENDATION_CONFIG = {
  missing: {
    title: "Пропущенные значения",
    color: "#D9444A",
    text: "В данных обнаружены пропущенные значения. Проверьте пустые ячейки и заполните их корректными значениями или удалите строки, в которых данные отсутствуют",
  },

  duplicate_row: {
    title: "Повторяющиеся данные",
    color: "#D7DF55",
    text: "В данных обнаружены повторяющиеся строки. Проверьте дубликаты и удалите записи, которые не должны повторяться",
  },

  invalid_value: {
    title: "Некорректные значения",
    color: "#169BD5",
    text: "В данных обнаружены значения, которые не соответствуют ожидаемому формату. Проверьте их и исправьте некорректные данные",
  },

  inconsistency: {
    title: "Несогласованности",
    color: "#E17A21",
    text: "В данных обнаружены несогласованности. Проверьте связанные значения и приведите их к единому формату",
  },
};

function Recommendations({ issues = [] }) {
  const groupedIssues = issues.reduce((result, issue) => {
    const type = issue.type;
    const count = Number(issue.count) || 0;

    if (!result[type]) {
      result[type] = {
        type,
        count: 0,
        columns: [],
      };
    }

    result[type].count += count;

    if (issue.column && !result[type].columns.includes(issue.column)) {
      result[type].columns.push(issue.column);
    }

    return result;
  }, {});

  const recommendations = Object.values(groupedIssues).filter(
    (item) => RECOMMENDATION_CONFIG[item.type]
  );

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
          {recommendations.map((item) => {
            const config = RECOMMENDATION_CONFIG[item.type];

            return (
              <div className="recommendation-card" key={item.type} >
                <div
                  className="recommendation-indicator"
                  style={{ backgroundColor: config.color }}
                />

                <div className="recommendation-content">
                  <div className="recommendation-header">
                    <h3>{config.title}</h3>
                  </div>
                  <p>{config.text}</p>
                </div>

              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default Recommendations;