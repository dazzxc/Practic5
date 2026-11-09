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
                        <svg width="32" height="35" viewBox="0 0 32 35" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11 33.1667V17.3333H20.5V33.1667M1.5 12.5833L15.75 1.5L30 12.5833V30C30 30.8399 29.6664 31.6453 29.0725 32.2392C28.4786 32.833 27.6732 33.1667 26.8333 33.1667H4.66667C3.82681 33.1667 3.02136 32.833 2.4275 32.2392C1.83363 31.6453 1.5 30.8399 1.5 30V12.5833Z" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke="white"/>
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
                        <svg width="29" height="35" viewBox="0 0 29 35" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M1.5 29.2083C1.5 28.1585 1.91704 27.1517 2.65937 26.4094C3.4017 25.667 4.40852 25.25 5.45833 25.25H26.8333M1.5 29.2083C1.5 30.2581 1.91704 31.265 2.65937 32.0073C3.4017 32.7496 4.40852 33.1667 5.45833 33.1667H26.8333V1.5H5.45833C4.40852 1.5 3.4017 1.91704 2.65937 2.65937C1.91704 3.4017 1.5 4.40852 1.5 5.45833V29.2083Z" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke="#B3B3B3"/>
</svg>                   
                    </span>
                    <span>Отчёты</span>
                </NavLink>
            </nav>
        </aside>

    );
}

export default Sidebar;