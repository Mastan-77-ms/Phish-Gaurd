import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import "./App.css";
import Header from "./Header";
import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import History from "./pages/History";

export default function App() {
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.classList.toggle("light-theme", savedTheme === "light");
    return savedTheme;
  });

  const [showHistory, setShowHistory] = useState(true);
  const [lastScanResult, setLastScanResult] = useState(null);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("light-theme", newTheme === "light");
  };

  const handleScanResult = (result) => {
    setLastScanResult(result);
    // Only store in memory, not persisted - will clear on page reload
  };

  return (
    <div className="app">
      <Header 
        theme={theme}
        onToggleTheme={toggleTheme}
        showHistory={showHistory}
        onToggleHistory={() => setShowHistory(!showHistory)}
      />
      
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard showHistory={showHistory} lastScanResult={lastScanResult} onClearResult={() => setLastScanResult(null)} />} />
          <Route path="/analyze" element={<Analyze onScanComplete={handleScanResult} />} />
          <Route path="/history" element={<History onRescan={handleScanResult} />} />
        </Routes>
      </div>
    </div>
  );
}
