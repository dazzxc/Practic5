import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MainPage from "./Pages/MainPage";
import ReportPage from "./Pages/ReportPage";
import ReportDetailPage from "./Pages/ReportDetailPage";
import "./App.css";

function App() {
return (
<div className="app">
<Sidebar />

  <main className="main-content">
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