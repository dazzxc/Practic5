import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MainPage from "./Pages/MainPage";
import ReportPage from "./Pages/ReportPage";
import ReportDetailPage from "./Pages/ReportDetailPage";
import styles from "./App.module.css";

function App() {
return (
<div className={styles.app}>
<Sidebar />

  <main className={styles.mainContent}>
    <Routes>
      <Route
        path="/"
        element={<MainPage />}
      />

      <Route
        path="/reports"
        element={<ReportPage />}
      />

      <Route
        path="/reports/:reportId"
        element={<ReportDetailPage />}
      />
    </Routes>
  </main>
</div>

);
}

export default App;