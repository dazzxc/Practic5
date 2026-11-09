import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MainPage from "./Pages/MainPage";
import ReportPage from "./Pages/ReportPage";
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
    </Routes>
  </main>
</div>

);
}

export default App;