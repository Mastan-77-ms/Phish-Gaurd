import { Link, useLocation } from "react-router-dom";
import "./Header.css";

export default function Header({ theme, onToggleTheme, showHistory, onToggleHistory }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-brand">
        <div className="brand-icon">⚔️</div>
        <div className="brand-text">
          <h2 className="brand-name">PhishGuard </h2>
          <p className="brand-tagline">ML-Trained Phishing Detection</p>
        </div>
      </div>

      <nav className="header-nav">
        <Link 
          to="/" 
          className={`nav-link ${isActive("/") ? "active" : ""}`}
        >
          <span className="nav-icon">📊</span>
          <span className="nav-text">Dashboard</span>
        </Link>
        
        <Link 
          to="/analyze" 
          className={`nav-link ${isActive("/analyze") ? "active" : ""}`}
        >
          <span className="nav-icon">🔍</span>
          <span className="nav-text">URL Analyse</span>
        </Link>
        
        <Link 
          to="/history" 
          className={`nav-link ${isActive("/history") ? "active" : ""}`}
        >
          <span className="nav-icon">📜</span>
          <span className="nav-text">History</span>
        </Link>
      </nav>

      <div className="header-controls">
        <button className="header-toggle-btn history-btn" onClick={onToggleHistory} title="Toggle History">
          <span className="toggle-icon">👁️</span>
          {showHistory ? "Hide" : "Show"}
        </button>
        <button className="header-toggle-btn theme-btn" onClick={onToggleTheme} title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Theme`}>
          <span className="theme-icon">{theme === 'dark' ? '☀️' : '🌙'}</span>
        </button>
      </div>
    </header>
  );
}
