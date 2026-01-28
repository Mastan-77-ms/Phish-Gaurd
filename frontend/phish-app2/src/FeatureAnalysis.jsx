import "./FeatureAnalysis.css";

export default function FeatureAnalysis({ features }) {
  if (!features || Object.keys(features).length === 0) {
    return null;
  }

  // Get total feature risk
  const totalRisk = features.total_feature_risk || 0;
  
  // Remove total_feature_risk from display list
  const displayFeatures = Object.keys(features).filter(k => k !== 'total_feature_risk');
  
  // Split features into two columns
  const midPoint = Math.ceil(displayFeatures.length / 2);
  const leftFeatures = displayFeatures.slice(0, midPoint);
  const rightFeatures = displayFeatures.slice(midPoint);

  const formatFeatureName = (key) => {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const FeatureItem = ({ feature, data }) => {
    const bgColor = data.safe ? 'feature-safe' : 'feature-suspicious';
    const icon = data.icon || (data.safe ? '✓' : '✗');
    const iconClass = data.safe ? 'icon-safe' : 'icon-suspicious';
    const riskScore = data.risk_score || 0;

    return (
      <div className={`feature-item ${bgColor}`}>
        <div className="feature-header">
          <span className={`feature-icon ${iconClass}`}>{icon}</span>
          <div className="feature-info">
            <span className="feature-label">{formatFeatureName(feature)}</span>
            <span className="feature-value">{data.value}</span>
          </div>
        </div>
        {riskScore > 0 && (
          <span className="risk-badge">+{riskScore} pts</span>
        )}
      </div>
    );
  };

  return (
    <div className="feature-analysis">
      <div className="feature-title-section">
        <h3 className="feature-title">🔍 Detailed Analysis</h3>
        <div className="total-risk-display">
          <span className="total-risk-label">Feature Risk Contribution:</span>
          <span className={`total-risk-score ${totalRisk > 50 ? 'high' : totalRisk > 25 ? 'medium' : 'low'}`}>
            {totalRisk} pts
          </span>
        </div>
      </div>
      
      <div className="features-grid">
        <div className="features-column">
          {leftFeatures.map(feature => (
            <FeatureItem
              key={feature}
              feature={feature}
              data={features[feature]}
            />
          ))}
        </div>
        
        <div className="features-column">
          {rightFeatures.map(feature => (
            <FeatureItem
              key={feature}
              feature={feature}
              data={features[feature]}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
