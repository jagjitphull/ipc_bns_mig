import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import LandingPage from './LandingPage';

function Dashboard() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Show landing page for non-authenticated users
  if (!isAuthenticated) {
    return <LandingPage />;
  }

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await apiService.getStats();
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load statistics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Navigation handlers for clickable cards
  const handleSectionsClick = () => {
    navigate('/analyze');
  };

  const handleChangesClick = () => {
    // Navigate to analyzer with a hint to search changed sections
    navigate('/analyze', { state: { filter: 'changes' } });
  };

  const handleRepealedClick = () => {
    // Navigate to analyzer to search repealed section (497)
    navigate('/analyze', { state: { filter: 'repealed' } });
  };

  const handleCasesClick = () => {
    navigate('/cases');
  };

  if (loading) {
    return <div className="loading">Loading statistics...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard">
      <div className="hero-section">
        <h2>IPC to BNS Transition Analysis System</h2>
        <p className="hero-description">
          Comprehensive legal reasoning agent for analyzing the transition from
          Indian Penal Code (IPC) to Bhartiya Nyaya Sanhita (BNS) with AI-powered
          case law retrieval and validity warnings.
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card clickable" onClick={handleSectionsClick} title="Click to go to Section Analyzer">
          <div className="stat-number">{stats?.total_ipc_sections || 0}</div>
          <div className="stat-label">Total IPC Sections</div>
          <div className="card-hint">Click to analyze →</div>
        </div>

        <div className="stat-card highlight clickable" onClick={handleChangesClick} title="Click to view sections with changes">
          <div className="stat-number">{stats?.sections_with_changes || 0}</div>
          <div className="stat-label">Sections with Changes</div>
          <div className="card-hint">Click to explore →</div>
        </div>

        <div className="stat-card warning clickable" onClick={handleRepealedClick} title="Click to view repealed sections">
          <div className="stat-number">{stats?.repealed_sections || 0}</div>
          <div className="stat-label">Repealed Sections</div>
          <div className="card-hint">Click to view →</div>
        </div>

        <div className="stat-card clickable" onClick={handleCasesClick} title="Click to go to Case Search">
          <div className="stat-number">{stats?.total_landmark_cases || 0}</div>
          <div className="stat-label">Landmark Cases</div>
          <div className="card-hint">Click to search →</div>
        </div>
      </div>

      <div className="features-section">
        <h3>Key Features</h3>

        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h4>Section Analysis</h4>
            <p>
              Compare IPC sections with their BNS equivalents. Identify doctrinal
              changes, amendments, and repealed provisions.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h4>RAG-Powered Case Law</h4>
            <p>
              Semantic search over landmark cases using Retrieval Augmented Generation.
              Find relevant precedents instantly.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚖️</div>
            <h4>Validity Warnings</h4>
            <p>
              Automated assessment of precedent validity under BNS. Identifies cases
              requiring review or with questionable applicability.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h4>Legal Memos</h4>
            <p>
              Generate comprehensive lawyer-style memoranda with detailed analysis,
              precedents, and recommendations.
            </p>
          </div>
        </div>
      </div>

      <div className="info-section">
        <h3>About the System</h3>
        <div className="info-content">
          <p>
            This AI-powered legal reasoning agent assists lawyers and legal professionals
            in navigating the transition from the Indian Penal Code (IPC, 1860) to the
            Bhartiya Nyaya Sanhita (BNS, 2023).
          </p>
          <p>
            The system combines:
          </p>
          <ul>
            <li><strong>Structured Database:</strong> Complete IPC↔BNS mapping with 20+ major sections</li>
            <li><strong>RAG System:</strong> Vector-based semantic search over 12+ landmark cases</li>
            <li><strong>Legal Reasoning:</strong> AI agent that analyzes doctrinal changes and generates warnings</li>
            <li><strong>Memo Generation:</strong> Professional legal memoranda with validity assessments</li>
          </ul>
          <p className="warning-text">
            ⚠️ <strong>Important:</strong> This is an automated analysis tool. All outputs should
            be reviewed by qualified legal professionals before use in legal proceedings.
          </p>
        </div>
      </div>

      <div className="change-summary">
        <h3>Change Rate Analysis</h3>
        <div className="change-rate-display">
          <div className="change-rate-bar">
            <div
              className="change-rate-fill"
              style={{width: stats?.change_rate || '0%'}}
            >
              {stats?.change_rate || '0%'}
            </div>
          </div>
          <p>of IPC sections have substantive or procedural changes in BNS</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
