//<<<<<<< HEAD
import { useState } from 'react'
//=======
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
            <div className='icon-upload'>
                <svg width="132" height="132" viewBox="0 0 132 132" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M126.894 86.2629V113.35C126.894 116.943 125.467 120.387 122.927 122.927C120.387 125.467 116.943 126.894 113.35 126.894H18.5438C14.9518 126.894 11.5068 125.467 8.96689 122.927C6.42693 120.387 5 116.943 5 113.35V86.2629M99.8067 52.4033L65.9471 86.2629L32.0876 52.4033M65.9471 86.2629V5" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke="#3734C7"/>
</svg>
            </div>

            <h2 className="text-title"> Перетащите файл сюда </h2>

            <p className="text-subtitle"> 
                Или <span class="text-blue">выберите файл</span> на компьютере 
            </p>
        </div>

        <button className="primary-button"> <svg className='icon-file-choose' width="25" height="23" viewBox="0 0 25 23" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2.47658 22.2892C1.79552 22.2892 1.21249 22.0164 0.727496 21.4708C0.242499 20.9252 0 20.2693 0 19.5031V2.78615C0 2.01996 0.242499 1.36406 0.727496 0.818433C1.21249 0.272811 1.79552 0 2.47658 0H9.90633L12.3829 2.78615H22.2892C22.9703 2.78615 23.5533 3.05897 24.0383 3.60459C24.5233 4.15021 24.7658 4.80612 24.7658 5.57231V19.5031C24.7658 20.2693 24.5233 20.9252 24.0383 21.4708C23.5533 22.0164 22.9703 22.2892 22.2892 22.2892H2.47658ZM2.47658 19.5031H22.2892V5.57231H11.3613L8.88474 2.78615H2.47658V19.5031Z" fill="white"/>
</svg>
 Выбрать файл </button>  

        {/* Иконку для кнопки поставить и чутка поправить расположение карточки !!!*/}

    </div>
    </section>

);
}

export default MainPage;
//>>>>>>> c0b3f880eab7eae5640ecb97f6752eec572cfe1e
