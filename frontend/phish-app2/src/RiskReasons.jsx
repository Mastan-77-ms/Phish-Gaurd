import "./RiskReasons.css";

export default function RiskReasons({ reasons, status }) {
  // Define all security checks that should be shown
  const allSecurityChecks = [
    { id: "https", label: "HTTPS/SSL Encryption", icon: "🔒" },
    { id: "tld", label: "Legitimate Top-Level Domain", icon: "🌐" },
    { id: "subdomain", label: "Valid Subdomain Structure", icon: "🔗" },
    { id: "keywords", label: "No Phishing Keywords", icon: "🔍" },
    { id: "characters", label: "No Unsafe Characters", icon: "⚠️" },
    { id: "ip", label: "Uses Domain Name (Not IP)", icon: "📍" },
    { id: "length", label: "Normal URL Length", icon: "📏" }
  ];

  // Categorize reasons by check type
  const getCheckStatus = () => {
    const checks = {};
    
    // Initialize all checks as satisfied
    allSecurityChecks.forEach(check => {
      checks[check.id] = {
        satisfied: true,
        reasons: [],
        details: check
      };
    });

    // Mark unsatisfied checks based on reasons
    if (reasons && reasons.length > 0) {
      reasons.forEach(reason => {
        const reasonLower = reason.toLowerCase();
        
        // Check if reason is positive ([+]) or negative (→ or [HIGH RISK])
        const isPositiveReason = reason.includes("[+]");
        const isNegativeReason = reason.includes("→") || reasonLower.includes("[high risk]") || reasonLower.includes("[warn]") || reasonLower.includes("critical");
        
        if (reasonLower.includes("protocol") && (reasonLower.includes("invalid") || reasonLower.includes("instead"))) {
          // Invalid protocol is always a FAILURE, even without "→" marker
          const isCriticalProtocolIssue = reasonLower.includes("invalid");
          checks["https"].satisfied = isCriticalProtocolIssue ? false : !isNegativeReason;
          checks["https"].reasons.push(reason);
        } else if (reasonLower.includes("tld") || reasonLower.includes("top level domain")) {
          checks["tld"].satisfied = isPositiveReason ? true : !isNegativeReason;
          checks["tld"].reasons.push(reason);
        } else if (reasonLower.includes("subdomain")) {
          checks["subdomain"].satisfied = isPositiveReason ? true : !isNegativeReason;
          checks["subdomain"].reasons.push(reason);
        } else if (reasonLower.includes("keyword")) {
          checks["keywords"].satisfied = isPositiveReason ? true : !isNegativeReason;
          checks["keywords"].reasons.push(reason);
        } else if (reasonLower.includes("character") || reasonLower.includes("unsafe")) {
          checks["characters"].satisfied = isPositiveReason ? true : !isNegativeReason;
          checks["characters"].reasons.push(reason);
        } else if (reasonLower.includes("ip") || reasonLower.includes("domain name")) {
          // IP check: PASS if positive ([+]), FAIL if contains critical IP address warning
          const isCriticalIPFailure = reasonLower.includes("critical") && reasonLower.includes("ip address");
          checks["ip"].satisfied = isPositiveReason ? true : (isCriticalIPFailure ? false : !isNegativeReason);
          checks["ip"].reasons.push(reason);
        } else if (reasonLower.includes("length")) {
          checks["length"].satisfied = isPositiveReason ? true : !isNegativeReason;
          checks["length"].reasons.push(reason);
        }
      });
    }

    return checks;
  };

  const checks = getCheckStatus();
  const isPhishing = status === "PHISHING";
  const isSuspicious = status === "SUSPICIOUS";
  const isSafe = status === "SAFE";

  const getHeaderIcon = () => {
    if (isPhishing) return "⚠️";
    if (isSuspicious) return "⚡";
    return "✓";
  };

  const getHeaderText = () => {
    if (isPhishing) return "Security Issues Found";
    if (isSuspicious) return "Potential Concerns";
    return "Security Checks Passed";
  };

  return (
    <div className={`risk-reasons-container ${status.toLowerCase()}`}>
      <div className="reasons-header">
        <span className="header-icon">{getHeaderIcon()}</span>
        <span className="header-title">{getHeaderText()}</span>
        <span className="reasons-count">
          {reasons && reasons.length > 0 
            ? `(${reasons.length} ${reasons.length === 1 ? 'Issue' : 'Issues'} Found)` 
            : '(All Checks Passed)'}
        </span>
      </div>

      <div className="security-checks">
        {Object.entries(checks).map(([checkId, checkData], index) => (
          <div 
            key={checkId} 
            className={`security-check ${checkData.satisfied ? 'satisfied' : 'unsatisfied'}`}
            style={{ '--delay': `${index * 0.05}s` }}
          >
            <div className="check-header">
              <span className="check-icon">{checkData.details.icon}</span>
              <span className="check-label">{checkData.details.label}</span>
              <span className={`check-status ${checkData.satisfied ? 'pass' : 'fail'}`}>
                {checkData.satisfied ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            
            {checkData.reasons.length > 0 && (
              <div className="check-details">
                <ul className="reasons-list">
                  {checkData.reasons.map((reason, idx) => (
                    <li key={idx} className="reason-detail">
                      <span className="reason-indicator">→</span>
                      <span className="reason-text">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>

      {isPhishing && (
        <div className="action-recommendation phishing">
          <strong>⛔ Recommendation:</strong> Do not click this link. This URL appears to be a phishing attempt designed to steal your personal information. Multiple security checks have failed.
        </div>
      )}
      {isSuspicious && (
        <div className="action-recommendation suspicious">
          <strong>⚠️ Recommendation:</strong> Be cautious. This URL shows some suspicious characteristics. Verify the sender and website before entering credentials. Some security checks have concerns.
        </div>
      )}
      {isSafe && (
        <div className="action-recommendation safe">
          <strong>✓ Recommendation:</strong> This URL appears safe. All security checks have passed. However, always stay alert and never enter passwords on unexpected pages.
        </div>
      )}
    </div>
  );
}
