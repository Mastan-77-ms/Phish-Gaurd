import { useEffect, useState, useCallback } from "react";
import "../Dashboard.css";

export default function Dashboard({ showHistory, lastScanResult, onClearResult }) {
  const [history, setHistory] = useState([]);

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:3001/api/history");
      const data = await res.json();
      setHistory(data);
    } catch (error) {
      console.error("Error loading history:", error);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadHistory();
  }, [loadHistory]);

  const stats = {
    totalScans: history.length,
    phishingLinks: history.filter(item => item.status === "PHISHING").length,
    suspiciousLinks: history.filter(item => item.status === "SUSPICIOUS").length,
    safeLinks: history.filter(item => item.status === "SAFE").length
  };

  const phishingRatio = stats.totalScans === 0 ? 0 : ((stats.phishingLinks / stats.totalScans) * 100).toFixed(2);

  return (
    <div className="dashboard-container">
      <h2 className="dashboard-title">Security Dashboard</h2>
      
      {/* Show Recent Scan Result if available */}
      {lastScanResult && (
        <div className={`recent-result ${lastScanResult.isPhishing ? "phishing" : lastScanResult.isSuspicious ? "suspicious" : "safe"}`}>
          <div className="result-left">
            <div 
              className={`risk-circle ${lastScanResult.score >= 70 ? "high-risk-glow" : lastScanResult.score >= 40 ? "medium-risk-glow" : "low-risk-glow"}`}
              style={{
                boxShadow: lastScanResult.score >= 70 
                  ? "0 0 30px rgba(255, 0, 0, 0.6), 0 0 60px rgba(255, 0, 0, 0.3)"
                  : lastScanResult.score >= 40
                  ? "0 0 30px rgba(255, 152, 0, 0.6), 0 0 60px rgba(255, 152, 0, 0.3)"
                  : "0 0 30px rgba(76, 175, 80, 0.6), 0 0 60px rgba(76, 175, 80, 0.3)"
              }}
            >
              <svg viewBox="0 0 100 100" className="progress-ring-svg">
                <circle cx="50" cy="50" r="45" className="progress-ring-bg" />
                <circle cx="50" cy="50" r="45" className="progress-ring" 
                  style={{ '--percentage': lastScanResult.score }} />
              </svg>
              <div 
                className="risk-score"
                style={{
                  color: lastScanResult.score >= 70 
                    ? '#ff0000' 
                    : lastScanResult.score >= 30
                    ? '#ff9800'
                    : '#4caf50'
                }}
              >
                {lastScanResult.score}%
              </div>
              <div className="risk-label">Risk Score</div>
            </div>
          </div>

          <div className="result-right">
            <div className={`status-indicator ${lastScanResult.isPhishing ? "threat" : lastScanResult.isSuspicious ? "caution" : "safe"}`}>
              <span className="status-icon">{lastScanResult.isPhishing ? "⚠️" : lastScanResult.isSuspicious ? "⚡" : "✓"}</span>
              <span className="status-text">{lastScanResult.isPhishing ? "HIGH RISK" : lastScanResult.isSuspicious ? "MEDIUM RISK" : "LOW RISK"}</span>
            </div>
            <p className="result-url">{lastScanResult.url}</p>
            <div className={`status-badge ${lastScanResult.isPhishing ? "malicious" : lastScanResult.isSuspicious ? "suspicious" : "safe"}`}>
              Status: {lastScanResult.isPhishing ? "MALICIOUS" : lastScanResult.isSuspicious ? "SUSPICIOUS" : "SAFE"}
            </div>
            <button className="close-result-btn" onClick={onClearResult}>✕ Clear</button>
          </div>
        </div>
      )}
      
      <div className="stats-grid">
        {/* Total Scans Card */}
        <div className="stat-card total-scans">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Total Analyzed</h3>
            <p className="stat-number">🛡️ {stats.totalScans}</p>
            <p className="stat-label">URLs Scanned</p>
          </div>
        </div>

        {/* Safe Links Card */}
        <div className="stat-card safe-links">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Secure</h3>
            <p className="stat-number">✅ {stats.safeLinks}</p>
            <p className="stat-label">Verified Safe</p>
          </div>
        </div>

        {/* Phishing Links Card */}
        <div className="stat-card phishing-links">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Threats</h3>
            <p className="stat-number">⚠️ {stats.phishingLinks}</p>
            <p className="stat-label">Detected</p>
          </div>
        </div>

        {/* Suspicious Card */}
        <div className="stat-card suspicious-links">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Suspicious</h3>
            <p className="stat-number">⚡ {stats.suspiciousLinks}</p>
            <p className="stat-label">Requires Caution</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-section">
        <h3>Security Distribution</h3>
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-safe" 
              style={{ width: `${stats.totalScans === 0 ? 0 : (stats.safeLinks / stats.totalScans) * 100}%` }}
            >
              <span className="progress-label">
                {stats.totalScans === 0 ? "0%" : `${((stats.safeLinks / stats.totalScans) * 100).toFixed(1)}%`}
              </span>
            </div>
            <div 
              className="progress-suspicious" 
              style={{ width: `${stats.totalScans === 0 ? 0 : (stats.suspiciousLinks / stats.totalScans) * 100}%` }}
            >
              <span className="progress-label">
                {stats.totalScans === 0 ? "0%" : `${((stats.suspiciousLinks / stats.totalScans) * 100).toFixed(1)}%`}
              </span>
            </div>
            <div 
              className="progress-phishing" 
              style={{ width: `${stats.totalScans === 0 ? 0 : (stats.phishingLinks / stats.totalScans) * 100}%` }}
            >
              <span className="progress-label">
                {stats.totalScans === 0 ? "0%" : `${((stats.phishingLinks / stats.totalScans) * 100).toFixed(1)}%`}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Card */}
      <div className="summary-card">
        <h3>Analysis Summary</h3>
        <p>
          Total URLs analyzed: <strong>{stats.totalScans}</strong> | 
          <span className="safe-text"> {stats.safeLinks} secure</span> | 
          <span className="suspicious-text"> {stats.suspiciousLinks} suspicious</span> | 
          <span className="phishing-text"> {stats.phishingLinks} threats detected</span>
        </p>
        <p>
          Overall threat detection rate: <strong>{phishingRatio}%</strong>
        </p>
      </div>

      {/* History Section */}
      {showHistory && (
        <div className="history-section" style={{ marginTop: "2rem" }}>
          <h3>Recent Scan History</h3>
          <div className="activity-list">
            {history.length === 0 ? (
              <p className="no-activity">No scan history yet. Start by analyzing a URL!</p>
            ) : (
              history.slice(0, 10).reverse().map((item) => (
                <div key={item._id} className={`activity-item ${item.status.toLowerCase()}`}>
                  <span className="activity-icon">
                    {item.status === "PHISHING" ? "⚠️" : item.status === "SUSPICIOUS" ? "⚡" : "✓"}
                  </span>
                  <div className="activity-details">
                    <p className="activity-url">{item.url}</p>
                    <p className="activity-time">
                      {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="activity-badge">
                    <span className={`status-badge ${item.status.toLowerCase()}`}>
                      {item.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
