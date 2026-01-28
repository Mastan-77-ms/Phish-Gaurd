import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import HistoryByCategory from "../HistoryByCategory";
import "./History.css";

export default function History({ onRescan }) {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedUrlDetails, setExpandedUrlDetails] = useState(null);
  const [detailedScans, setDetailedScans] = useState([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await fetch("http://localhost:3001/api/history");
      const data = await res.json();
      setHistory(data);
    } catch (error) {
      console.error("Error loading history:", error);
    }
  };

  const deleteHistoryItem = async (id) => {
    try {
      await fetch(`http://localhost:3001/api/history/${id}`, {
        method: "DELETE"
      });
      setHistory(history.filter(item => item._id !== id));
      setExpandedUrlDetails(null);
      loadHistory();
    } catch (error) {
      console.error("Error deleting history item:", error);
      alert("Failed to delete history item");
      loadHistory();
    }
  };

  const closeDetailedView = () => {
    setExpandedUrlDetails(null);
    setDetailedScans([]);
  };

  const rescanUrl = async (urlToScan) => {
    setLoading(true);
    if (!urlToScan.includes("://")) {
      setLoading(false);
      return alert("⚠️ Protocol Missing!\n\nThe URL does not have a protocol.");
    }

    try {
      const res = await fetch("http://localhost:3001/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlToScan })
      });

      const result = await res.json();
      // Call the onRescan callback to pass result to parent and show on dashboard
      if (onRescan) {
        onRescan({
          url: urlToScan,
          score: result.risk_score,
          isPhishing: result.status === "PHISHING",
          isSuspicious: result.status === "SUSPICIOUS",
          isSafe: result.status === "SAFE",
          timestamp: new Date().toISOString()
        });
      }
      loadHistory();
      alert("URL rescanned successfully!");
      // Navigate to dashboard using React Router (no full page reload)
      navigate("/");
    } catch (error) {
      alert("Error rescanning URL: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="history-page">
      <div className="history-content">
        <div className="history-header">
          <h1>Scan History</h1>
          <p className="history-subtitle">All your URL analysis records</p>
        </div>

        {history.length === 0 ? (
          <div className="no-history">
            <div className="no-history-icon">📜</div>
            <h2>No History Yet</h2>
            <p>Start scanning URLs to build your history!</p>
          </div>
        ) : (
          <div className="history-section show">
            <HistoryByCategory 
              history={history}
              onRescan={rescanUrl}
              onDelete={deleteHistoryItem}
              loading={loading}
            />
          </div>
        )}

        {expandedUrlDetails && (
          <div className="detailed-scan-overlay">
            <div className="detailed-scan-modal">
              <div className="detailed-scan-header">
                <h2>Scan History</h2>
                <p className="detailed-url">{expandedUrlDetails}</p>
                <button className="close-btn" onClick={closeDetailedView}>✕</button>
              </div>
              
              <div className="detailed-scan-content">
                {detailedScans.length === 0 ? (
                  <p className="no-scans">No scan records found</p>
                ) : (
                  <div className="scans-timeline">
                    {detailedScans.map((scan, index) => (
                      <div key={index} className={`scan-entry ${scan.status === "SAFE" ? "safe" : "phishing"}`}>
                        <div className="scan-entry-header">
                          <span className="scan-number">Scan #{detailedScans.length - index}</span>
                          <span className="scan-date">
                            {new Date(scan.timestamp).toLocaleString()}
                          </span>
                        </div>
                        
                        <div className="scan-details-grid">
                          <div className="detail-item">
                            <label>Risk Score</label>
                            <div className="score-display">
                              <span className="score-value">{scan.risk_score}%</span>
                              <div className="score-bar">
                                <div 
                                  className={`score-fill ${scan.status === "SAFE" ? "safe" : "phishing"}`}
                                  style={{ width: `${scan.risk_score}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="detail-item">
                            <label>Status</label>
                            <span className={`status-label ${scan.status === "SAFE" ? "safe" : "phishing"}`}>
                              {scan.status}
                            </span>
                          </div>
                          
                          <div className="detail-item">
                            <label>Risk Level</label>
                            <span className="risk-level">{scan.risk_label}</span>
                          </div>
                          
                          <div className="detail-item">
                            <label>Response Time</label>
                            <span className="response-time">{scan.response_time}s</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
