import { useState } from "react";
import "./HistoryByCategory.css";

export default function HistoryByCategory({ history, onRescan, onDelete, loading }) {
  const [expandedUrls, setExpandedUrls] = useState({});
  const [selectedUrl, setSelectedUrl] = useState(null);

  // Group history by URL
  const groupedHistory = history.reduce((acc, item) => {
    const url = item.url;
    if (!acc[url]) {
      acc[url] = [];
    }
    acc[url].push(item);
    return acc;
  }, {});

  // Sort each URL's scans by most recent first
  Object.keys(groupedHistory).forEach(url => {
    groupedHistory[url].sort((a, b) => {
      const dateA = new Date(a.timestamp || a.scanned_at || 0);
      const dateB = new Date(b.timestamp || b.scanned_at || 0);
      return dateB - dateA;
    });
  });

  const toggleExpand = (url) => {
    setExpandedUrls(prev => ({
      ...prev,
      [url]: !prev[url]
    }));
  };

  const deleteAllForUrl = async (url) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete all ${groupedHistory[url].length} scan records for this URL?\n\nThis action cannot be undone.`
    );
    
    if (confirmDelete) {
      for (const scan of groupedHistory[url]) {
        await onDelete(scan._id);
      }
    }
  };

  const getRiskColor = (score) => {
    if (score >= 70) return "#ff4040";      // Red - Phishing (70-100%)
    if (score >= 20) return "#ffa500";      // Orange - Suspicious (20-69%)
    return "#4caf50";                       // Green - Safe (0-19%)
  };

  const getRiskLabel = (score) => {
    if (score >= 70) return "🚩 PHISHING";
    if (score >= 20) return "⚠️ SUSPICIOUS";
    return "✓ SAFE";
  };

  if (Object.keys(groupedHistory).length === 0) {
    return <p className="empty-state">No analysis records. Start by entering a URL above.</p>;
  }

  const selectedUrlScans = selectedUrl ? groupedHistory[selectedUrl] : null;

  return (
    <>
      <div className="history-by-category">
        {Object.entries(groupedHistory).map(([url, scans]) => {
          const isExpanded = expandedUrls[url];
          const latestScan = scans[0];
          const scanCount = scans.length;

          return (
            <div key={url} className="url-category">
              <div 
                className="category-header"
                onClick={() => toggleExpand(url)}
                style={{ cursor: 'pointer' }}
              >
                <div className="category-header-left">
                  <span className="expand-icon">
                    {isExpanded ? "▼" : "▶"}
                  </span>
                  <span className="category-url">{url}</span>
                </div>
                
                <div className="category-header-right">
                  <span 
                    className="category-status"
                    style={{ 
                      backgroundColor: getRiskColor(latestScan.risk_score),
                      color: '#fff'
                    }}
                  >
                    {getRiskLabel(latestScan.risk_score)}
                  </span>
                  
                  <span className="category-score">
                    Latest: {latestScan.risk_score}%
                  </span>
                  
                  <span 
                    className="scan-count-badge"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedUrl(url);
                    }}
                    title="Click to view detailed history"
                    style={{ cursor: 'pointer' }}
                  >
                    {scanCount} scan{scanCount !== 1 ? 's' : ''} 📋
                  </span>

                  <button
                    className="rescan-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onRescan) {
                        onRescan(url);
                      }
                    }}
                    title="Rescan this URL"
                  >
                    🔄 Rescan
                  </button>

                  <button
                    className="delete-all-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteAllForUrl(url);
                    }}
                    title="Delete all scans for this URL"
                  >
                    🗑️ Delete All
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className="category-content">
                  {scans.map((scan, index) => (
                    <div 
                      key={index} 
                      className={`scan-item scan-${index + 1}`}
                    >
                      <div className="scan-item-header">
                        <span className="scan-number">
                          #{scanCount - index}
                        </span>
                        <span className="scan-timestamp">
                          {new Date(scan.timestamp || scan.scanned_at).toLocaleString()}
                        </span>
                      </div>

                      <div className="scan-item-details">
                        <div className="detail-cell">
                          <label>Risk Score</label>
                          <div className="score-bar">
                            <div 
                              className="score-fill"
                              style={{
                                width: `${scan.risk_score}%`,
                                backgroundColor: getRiskColor(scan.risk_score)
                              }}
                            />
                          </div>
                          <span className="score-text">{scan.risk_score}%</span>
                        </div>

                        <div className="detail-cell">
                          <label>Status</label>
                          <span className="status-text">
                            {getRiskLabel(scan.risk_score)}
                          </span>
                        </div>

                        <div className="detail-cell">
                          <label>Response Time</label>
                          <span className="response-time">{scan.response_time}s</span>
                        </div>
                      </div>

                      {scan.risk_reasons && scan.risk_reasons.length > 0 && (
                        <div className="scan-reasons">
                          <label>Detection Reasons:</label>
                          <ul className="reasons-list">
                            {scan.risk_reasons.slice(0, 3).map((reason, idx) => (
                              <li key={idx} className="reason-item">
                                {reason}
                              </li>
                            ))}
                            {scan.risk_reasons.length > 3 && (
                              <li className="reason-item more">
                                +{scan.risk_reasons.length - 3} more reasons
                              </li>
                            )}
                          </ul>
                        </div>
                      )}

                      <div className="scan-item-actions">
                        <button 
                          className="rescan-btn"
                          onClick={() => onRescan(url)}
                          disabled={loading}
                          title="Rescan this URL"
                        >
                          🔄 Rescan
                        </button>
                        <button 
                          className="delete-btn"
                          onClick={() => onDelete(scan._id)}
                          title="Delete this scan"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Modal Popup for Detailed History */}
      {selectedUrlScans && (
        <div className="history-modal-overlay" onClick={() => setSelectedUrl(null)}>
          <div className="history-modal-container" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="modal-header">
              <div className="modal-title-section">
                <h2 className="modal-title">📋 URL History - Detailed View</h2>
                <p className="modal-url" title={selectedUrl}>{selectedUrl}</p>
              </div>
              <button 
                className="modal-close-btn" 
                onClick={() => setSelectedUrl(null)} 
                title="Close"
              >
                ✕
              </button>
            </div>

            {/* Modal Stats Bar */}
            <div className="modal-stats-bar">
              <div className="stat-item">
                <span className="stat-label">Total Scans:</span>
                <span className="stat-value">{selectedUrlScans.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Latest Risk:</span>
                <span 
                  className="stat-risk"
                  style={{ backgroundColor: getRiskColor(selectedUrlScans[0].risk_score) }}
                >
                  {selectedUrlScans[0].risk_score}%
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Status:</span>
                <span className="stat-status">{getRiskLabel(selectedUrlScans[0].risk_score)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Last Scan:</span>
                <span className="stat-date">
                  {new Date(selectedUrlScans[0].timestamp || selectedUrlScans[0].scanned_at).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Modal Content */}
            <div className="modal-content">
              <div className="scans-list">
                {selectedUrlScans.map((scan, index) => (
                  <div key={index} className="scan-card">
                    <div className="scan-card-header">
                      <div className="scan-header-left">
                        <span className="scan-badge">Scan #{selectedUrlScans.length - index}</span>
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
                          <label className="reasons-label">🔍 Detection Categories:</label>
                          <ul className="reasons-list-modal">
                            {scan.risk_reasons.map((reason, idx) => (
                              <li key={idx} className="reason-item-modal">
                                <span className="reason-icon">→</span>
                                <span className="reason-text">{reason}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="scan-actions-modal">
                        <button 
                          className="action-btn rescan-btn"
                          onClick={() => {
                            onRescan(selectedUrl);
                            setSelectedUrl(null);
                          }}
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
            </div>

            {/* Modal Footer */}
            <div className="modal-footer">
              <button 
                className="footer-btn close" 
                onClick={() => setSelectedUrl(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
