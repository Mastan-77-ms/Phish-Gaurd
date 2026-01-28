import { useState } from "react";
import FeatureAnalysis from "../FeatureAnalysis";
import RiskReasons from "../RiskReasons";
import "./Analyze.css";

export default function Analyze({ onScanComplete }) {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const scanUrl = async () => {
    if (!url) return alert("Please enter a URL!");

    // Check if URL has protocol
    if (!url.includes("://")) {
      return alert("⚠️ Protocol Missing!\n\nPlease enter a URL with a protocol.\n\nExamples:\n• https://example.com\n• http://example.com");
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:3001/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      const data = await res.json();
      const result = {
        url: data.url,
        score: data.risk_score !== undefined ? data.risk_score : 0,
        isPhishing: data.status === "PHISHING",
        isSuspicious: data.status === "SUSPICIOUS",
        status: data.status,
        risk_label: data.risk_label,
        response_time: data.response_time,
        risk_reasons: data.risk_reasons || [],
        features: data.features || {}
      };
      setResult(result);
      // Pass scan result to parent App component
      if (onScanComplete) {
        onScanComplete(result);
      }
    } catch (error) {
      alert("Error scanning URL: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      scanUrl();
    }
  };

  return (
    <div className="analyze-page">
      <div className="analyze-content">
        <div className="scan-container">
          <h1>Scan URL for Threats</h1>
          <p className="scan-subtitle">Enter any URL to analyze for phishing attempts and malicious content</p>

          <div className="scan-form">
            <input
              type="text"
              value={url}
              onChange={e => setUrl(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter URL to analyze (e.g., https://example.com)"
              disabled={loading}
              className="url-input"
            />
            <button onClick={scanUrl} disabled={loading} className="scan-btn">
              {loading ? "Analyzing..." : "Scan Now"}
            </button>
          </div>

          {result && (
            <div className="analyze-result-container">
              <div className={`result ${result.isPhishing ? "phishing" : result.isSuspicious ? "suspicious" : "safe"}`}>
                <div className="result-left">
                  <div className="risk-circle">
                    <svg viewBox="0 0 100 100" className="progress-ring-svg">
                      <circle cx="50" cy="50" r="45" className="progress-ring-bg" />
                      <circle cx="50" cy="50" r="45" className="progress-ring" 
                        style={{ '--percentage': result.score }} />
                    </svg>
                    <div className="risk-score">{result.score}%</div>
                    <div className="risk-label">Risk Score</div>
                  </div>
                </div>

                <div className="result-right">
                  <div className={`status-indicator ${result.isPhishing ? "threat" : result.isSuspicious ? "caution" : "safe"}`}>
                    <span className="status-icon">{result.isPhishing ? "⚠️" : result.isSuspicious ? "⚡" : "✓"}</span>
                    <span className="status-text">{result.isPhishing ? "HIGH RISK" : result.isSuspicious ? "MEDIUM RISK" : "LOW RISK"}</span>
                  </div>
                  <p className="result-url">{result.url}</p>
                  <div className={`status-badge ${result.isPhishing ? "malicious" : result.isSuspicious ? "suspicious" : "safe"}`}>
                    Status: {result.isPhishing ? "MALICIOUS" : result.isSuspicious ? "SUSPICIOUS" : "SAFE"}
                  </div>
                  
                  {(result.isPhishing || result.isSuspicious || (result.risk_reasons && result.risk_reasons.length > 0)) && (
                    <RiskReasons reasons={result.risk_reasons || []} status={result.status} />
                  )}
                  
                  <details className="analysis-details" open={result.isPhishing || result.isSuspicious}>
                    <summary>Analysis Details</summary>
                    <p>{result.isPhishing ? "This URL has been flagged as potentially malicious. Avoid accessing this link." : result.isSuspicious ? "This URL has some suspicious characteristics. Exercise caution before accessing." : "This URL has passed security verification and is safe to access."}</p>
                  </details>
                </div>
              </div>

              <FeatureAnalysis features={result.features} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
