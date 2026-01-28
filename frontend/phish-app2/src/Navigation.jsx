import { Link, useLocation } from "react-router-dom";
import "./Navigation.css";

export default function Navigation() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navigation">
      <div className="nav-container">
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
      </div>
    </nav>
  );
}
