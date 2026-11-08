import "./MainPage.css";

function MainPage() {  // главная страничка, пока что не доделанная 
return (
    <section className="page">
    <h1 className="page-title">
    Анализ качества данных
    </h1>

    <p className="page-subtitle"> Загрузите CSV или JSON файл, чтобы проверить его качество </p>

    <div className="upload-card">
        <div className="upload-area">
            <div > Иконку вставить</div>

            <h2 className="text-title"> Перетащите файл сюда </h2>

            <p className="text-subtitle"> 
                Или <span class="text-blue">выберите файл</span> на компьютере 
            </p>
        </div>

        <button className="primary-button"> Выбрать файл </button>  

        {/* Иконку для кнопки поставить и чутка поправить расположение карточки !!!*/}

    </div>
    </section>

);
}

export default MainPage;