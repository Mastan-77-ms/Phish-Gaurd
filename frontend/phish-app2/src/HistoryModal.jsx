import "./HistoryModal.css";

export default function HistoryModal({ url, scans, onClose, onRescan, onDelete, loading }) {
  if (!url || !scans) return null;

  const getRiskColor = (score) => {
    if (score >= 70) return "#ff4040";
    if (score >= 30) return "#ffa500";
    return "#4caf50";
  };

  const getRiskLabel = (score) => {
    if (score >= 70) return "🚩 PHISHING";
    if (score >= 30) return "⚠️ SUSPICIOUS";
    return "✓ SAFE";
  };

  const latestScan = scans[0];

  return (
    <div className="history-modal-overlay" onClick={onClose}>
      <div className="history-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-section">
            <h2 className="modal-title">URL History</h2>
            <p className="modal-url" title={url}>{url}</p>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="Close">✕</button>
        </div>

        {/* Modal Stats Bar */}
        <div className="modal-stats-bar">
          <div className="stat-item">
            <span className="stat-label">Total Scans:</span>
            <span className="stat-value">{scans.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Latest Risk:</span>
            <span 
              className="stat-risk"
              style={{ backgroundColor: getRiskColor(latestScan.risk_score) }}
            >
              {latestScan.risk_score}%
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Status:</span>
            <span className="stat-status">{getRiskLabel(latestScan.risk_score)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Last Scan:</span>
            <span className="stat-date">
              {new Date(latestScan.timestamp || latestScan.scanned_at).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Modal Content */}
        <div className="modal-content">
          {scans.length === 0 ? (
            <p className="no-scans-message">No scan records found</p>
          ) : (
            <div className="scans-list">
              {scans.map((scan, index) => (
                <div key={index} className="scan-card">
                  <div className="scan-card-header">
                    <div className="scan-header-left">
                      <span className="scan-badge">Scan #{scans.length - index}</span>
                      <span className="scan-date">
                        {new Date(scan.timestamp || scan.scanned_at).toLocaleString()}
                      </span>
                    </div>
                    <div 
                      className="scan-status-badge"
                      style={{ backgroundColor: getRiskColor(scan.risk_score) }}
                    >
                      {getRiskLabel(scan.risk_score)}
                    </div>
                  </div>

                  <div className="scan-card-body">
                    {/* Risk Score */}
                    <div className="scan-info-grid">
                      <div className="info-cell">
                        <label>Risk Score</label>
                        <div className="score-display">
                          <div className="score-bar-container">
                            <div 
                              className="score-bar-fill"
                              style={{
                                width: `${scan.risk_score}%`,
                                backgroundColor: getRiskColor(scan.risk_score)
                              }}
                            />
                          </div>
                          <span className="score-percentage">{scan.risk_score}%</span>
                        </div>
                      </div>

                      <div className="info-cell">
                        <label>Status</label>
                        <span className="status-value">{scan.status}</span>
                      </div>

                      <div className="info-cell">
                        <label>Response Time</label>
                        <span className="time-value">{scan.response_time}s</span>
                      </div>
                    </div>

                    {/* Risk Reasons */}
                    {scan.risk_reasons && scan.risk_reasons.length > 0 && (
                      <div className="reasons-section">
                        <label className="reasons-label">Detection Reasons:</label>
                        <ul className="reasons-list">
                          {scan.risk_reasons.map((reason, idx) => (
                            <li key={idx} className="reason-item">
                              <span className="reason-icon">→</span>
                              <span className="reason-text">{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="scan-actions">
                      <button 
                        className="action-btn rescan-btn"
                        onClick={() => onRescan(url)}
                        disabled={loading}
                        title="Rescan this URL"
                      >
                        🔄 Rescan
                      </button>
                      <button 
                        className="action-btn delete-btn"
                        onClick={() => onDelete(scan._id)}
                        title="Delete this scan"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button className="footer-btn close" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
