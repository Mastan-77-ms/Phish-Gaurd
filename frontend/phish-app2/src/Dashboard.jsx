import { useEffect, useState } from "react";
import "./Dashboard.css";

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalScans: 0,
    safeLinks: 0,
    phishingLinks: 0,
    phishingRatio: 0
  });
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const res = await fetch("http://localhost:3001/api/history");
      const data = await res.json();
      
      const totalScans = data.length;
      const phishingLinks = data.filter(item => item.status === "PHISHING").length;
      const safeLinks = totalScans - phishingLinks;
      const phishingRatio = totalScans === 0 ? 0 : ((phishingLinks / totalScans) * 100).toFixed(2);

      setStats({
        totalScans,
        safeLinks,
        phishingLinks,
        phishingRatio
      });
      setLoading(false);
    } catch (error) {
      console.error("Error fetching stats:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchStats();
  }, []);

  if (loading) {
    return <div className="dashboard-container loading">Loading Dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <h2 className="dashboard-title">Security Dashboard</h2>
      
      <div className="stats-grid">
        {/* Total Scans Card */}
        <div className="stat-card total-scans">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Total Analyzed</h3>
            <p className="stat-number">{stats.totalScans}</p>
            <p className="stat-label">URLs Scanned</p>
          </div>
        </div>

        {/* Safe Links Card */}
        <div className="stat-card safe-links">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Secure</h3>
            <p className="stat-number">{stats.safeLinks}</p>
            <p className="stat-label">Verified Safe</p>
          </div>
        </div>

        {/* Phishing Links Card */}
        <div className="stat-card phishing-links">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Threats</h3>
            <p className="stat-number">{stats.phishingLinks}</p>
            <p className="stat-label">Detected</p>
          </div>
        </div>

        {/* Phishing Ratio Card */}
        <div className="stat-card phishing-ratio">
          <div className="stat-icon-placeholder"></div>
          <div className="stat-content">
            <h3>Threat Rate</h3>
            <p className="stat-number">{stats.phishingRatio}%</p>
            <p className="stat-label">Detection Ratio</p>
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
          <span className="phishing-text"> {stats.phishingLinks} threats detected</span>
        </p>
        <p>
          Overall threat detection rate: <strong>{stats.phishingRatio}%</strong>
        </p>
      </div>
    </div>
  );
}
