import "./ReportPage.css";

function ReportPage() {   // страница для отчетов, пока что пустая
return (
<section className="page">
<h1 className="page-title">
Отчёт по анализу
</h1>

  <p className="page-subtitle">
    Список проверенных объектов
  </p>

  <div className="empty-report">
    Необходимые данные не найдены
  </div>
</section>

);
}

export default ReportPage;