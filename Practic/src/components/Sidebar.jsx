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
                            
                    <span className="nav-icon"> !!</span>
                    <span>Главная</span>
                </NavLink>

                <NavLink
                    to="/reports"
                    className={({ isActive }) =>
                    `nav-item ${isActive ? "active" : ""}`
                    }
                    >
                    <span className="nav-icon">!! </span>
                    <span>Отчёты</span>
                </NavLink>
            </nav>
        </aside>

    );
}

export default Sidebar;