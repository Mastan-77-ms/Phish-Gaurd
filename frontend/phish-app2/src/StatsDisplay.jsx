import { useEffect, useState } from "react";
import "./StatsDisplay.css";

export default function StatsDisplay({ history }) {
  const [stats, setStats] = useState({
    totalScans: 0,
    threatsBlocked: 0,
    safeUrls: 0,
    avgResponse: "< 0.5s"
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("http://localhost:3001/api/stats");
        const data = await res.json();
        setStats({
          totalScans: data.total_scans || 0,
          threatsBlocked: data.phishing_blocked || 0,
          safeUrls: data.safe_urls || 0,
          avgResponse: data.avg_response_time || "< 0.5s"
        });
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    };

    fetchStats();
  }, [history]);

  return (
    <div className="stats-display">
      <div className="stat-item total-scans">
        <div className="stat-label">TOTAL SCANS</div>
        <div className="stat-value">{stats.totalScans}</div>
        <div className="stat-icon">📊</div>
      </div>

      <div className="stat-item threats-blocked">
        <div className="stat-label">THREATS BLOCKED</div>
        <div className="stat-value">{stats.threatsBlocked}</div>
        <div className="stat-icon">🚨</div>
      </div>

      <div className="stat-item safe-urls">
        <div className="stat-label">SAFE URLS</div>
        <div className="stat-value">{stats.safeUrls}</div>
        <div className="stat-icon">✓</div>
      </div>

      <div className="stat-item avg-response">
        <div className="stat-label">AVG RESPONSE</div>
        <div className="stat-value">{stats.avgResponse}</div>
        <div className="stat-icon">⚡</div>
      </div>
    </div>
  );
}
