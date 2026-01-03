import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { apiService } from '../services/api';

function SectionAnalyzer() {
  const location = useLocation();
  const [ipcSection, setIpcSection] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestionText, setSuggestionText] = useState('');

  // Handle navigation from dashboard with filter state
  useEffect(() => {
    if (location.state?.filter) {
      const filter = location.state.filter;
      if (filter === 'changes') {
        setSuggestionText('Try: 124A (Sedition→Sovereignty), 304A (Death by negligence - enhanced punishment)');
      } else if (filter === 'repealed') {
        setSuggestionText('Try: 497 (Adultery - decriminalized and repealed)');
      }
    }
  }, [location]);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!ipcSection.trim()) {
      setError('Please enter an IPC section number');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await apiService.analyzeSection(ipcSection);
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze section');
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const getChangeTypeClass = (changeType) => {
    const classes = {
      'substantive': 'change-substantive',
      'procedural': 'change-procedural',
      'repealed': 'change-repealed',
      'linguistic': 'change-linguistic',
      'none': 'change-none'
    };
    return classes[changeType] || '';
  };

  const getValidityClass = (status) => {
    const classes = {
      'valid': 'validity-valid',
      'requires_review': 'validity-review',
      'questionable': 'validity-questionable',
      'invalid': 'validity-invalid'
    };
    return classes[status] || '';
  };

  return (
    <div className="section-analyzer">
      <h2>IPC Section Analyzer</h2>
      <p className="page-description">
        Analyze the transition of an IPC section to BNS, including doctrinal changes,
        relevant case law, and validity warnings.
      </p>

      <form onSubmit={handleAnalyze} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={ipcSection}
            onChange={(e) => setIpcSection(e.target.value)}
            placeholder="Enter IPC Section (e.g., 302, 420, 124A)"
            className="search-input"
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
        {suggestionText && (
          <div className="suggestion-box">
            💡 <strong>Suggestion:</strong> {suggestionText}
          </div>
        )}
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {analysis && (
        <div className="analysis-results">
          {/* IPC Section Details */}
          <div className="section-card">
            <h3>IPC Section {analysis.ipc_section}</h3>
            <div className="section-details">
              <div className="detail-row">
                <strong>Description:</strong>
                <span>{analysis.ipc_description}</span>
              </div>
              <div className="detail-row">
                <strong>Category:</strong>
                <span>{analysis.category}</span>
              </div>
              <div className="detail-row">
                <strong>Punishment:</strong>
                <span>{analysis.punishment}</span>
              </div>
              <div className="text-box">
                <strong>Full Text:</strong>
                <p>{analysis.ipc_text}</p>
              </div>
            </div>
          </div>

          {/* BNS Equivalent */}
          <div className="section-card">
            <h3>BNS Equivalent</h3>
            {analysis.bns_section ? (
              <div className="section-details">
                <div className="detail-row">
                  <strong>BNS Section:</strong>
                  <span className="bns-section">{analysis.bns_section}</span>
                </div>
                <div className="detail-row">
                  <strong>Description:</strong>
                  <span>{analysis.bns_description}</span>
                </div>
                <div className="text-box">
                  <strong>Full Text:</strong>
                  <p>{analysis.bns_text}</p>
                </div>
              </div>
            ) : (
              <div className="repealed-notice">
                ⚠️ This section has been REPEALED or NOT INCLUDED in BNS
              </div>
            )}
          </div>

          {/* Change Analysis */}
          <div className={`change-card ${getChangeTypeClass(analysis.change_type)}`}>
            <h3>Doctrinal Changes</h3>
            <div className="change-badge">
              {analysis.change_type.toUpperCase()}
            </div>
            <p className="change-summary">{analysis.change_summary}</p>

            {analysis.change_analysis?.implications?.length > 0 && (
              <div className="implications">
                <h4>Legal Implications:</h4>
                {analysis.change_analysis.implications.map((impl, idx) => (
                  <div key={idx} className="implication-item">
                    <div className="impl-header">
                      <span className={`severity-badge severity-${impl.severity}`}>
                        {impl.severity.toUpperCase()}
                      </span>
                      <span>{impl.type}</span>
                    </div>
                    <p>{impl.description}</p>
                    <p className="impl-effect"><strong>Effect:</strong> {impl.legal_effect}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Validity Warnings */}
          {analysis.validity_warnings?.length > 0 && (
            <div className="warnings-card">
              <h3>⚠️ Validity Warnings</h3>
              {analysis.validity_warnings.map((warning, idx) => (
                <div key={idx} className={`warning-item warning-${warning.level}`}>
                  <div className="warning-header">
                    <span className="warning-level">{warning.level.toUpperCase()}</span>
                    <span className="warning-type">{warning.type}</span>
                  </div>
                  <p className="warning-message">{warning.message}</p>
                  {warning.case && <p><strong>Case:</strong> {warning.case}</p>}
                  {warning.reasoning && <p><strong>Reasoning:</strong> {warning.reasoning}</p>}
                  {warning.recommendation && (
                    <p className="recommendation"><strong>Recommendation:</strong> {warning.recommendation}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Landmark Cases */}
          {analysis.landmark_cases?.length > 0 && (
            <div className="cases-card">
              <h3>Landmark Cases</h3>
              {analysis.landmark_cases.map((case_, idx) => (
                <div key={idx} className="case-item">
                  <h4>{case_.case_name}</h4>
                  <div className="case-meta">
                    <span>{case_.citation}</span>
                    <span>{case_.court} ({case_.year})</span>
                  </div>
                  <div className={`validity-badge ${getValidityClass(case_.validity_status)}`}>
                    {case_.validity_status.replace('_', ' ').toUpperCase()}
                  </div>
                  <p className="ratio"><strong>Ratio Decidendi:</strong> {case_.ratio_decidendi}</p>
                  {case_.validity_reasoning && (
                    <p className="validity-reason">
                      <strong>Validity Note:</strong> {case_.validity_reasoning}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SectionAnalyzer;
