import { NavLink } from "react-router-dom";
import "./Sidebar.css";

function Sidebar() {     //это всё менюшка слева да
    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                <NavLink
                    to="/"
                    className={({ isActive }) =>
                    `nav-item ${isActive ? "active" : ""}`
                    }
                    >
                            
                    <span className="nav-icon">
                        <svg width="27" height="30" viewBox="0 0 27 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9.5 28.1667V14.8333H17.5V28.1667M1.5 10.8333L13.5 1.5L25.5 10.8333V25.5C25.5 26.2072 25.219 26.8855 24.719 27.3856C24.2189 27.8857 23.5406 28.1667 22.8333 28.1667H4.16667C3.45942 28.1667 2.78115 27.8857 2.28105 27.3856C1.78095 26.8855 1.5 26.2072 1.5 25.5V10.8333Z" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke="white"/>
                        </svg>
                    </span>
                    <span>Главная</span>
                </NavLink>

                <NavLink
                    to="/reports"
                    className={({ isActive }) =>
                    `nav-item ${isActive ? "active" : ""}`
                    }
                    >
                    <span className="nav-icon">
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5.33325 26C5.33325 25.116 5.68444 24.2681 6.30956 23.643C6.93468 23.0179 7.78253 22.6667 8.66659 22.6667H26.6666M5.33325 26C5.33325 26.8841 5.68444 27.7319 6.30956 28.357C6.93468 28.9822 7.78253 29.3334 8.66659 29.3334H26.6666V2.66669H8.66659C7.78253 2.66669 6.93468 3.01788 6.30956 3.643C5.68444 4.26812 5.33325 5.11597 5.33325 6.00002V26Z" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke="#B3B3B3"/>
                        </svg>
                    </span>
                    <span>Отчёты</span>
                </NavLink>
            </nav>
        </aside>

    );
}

export default Sidebar;