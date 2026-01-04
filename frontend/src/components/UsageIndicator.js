import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './UsageIndicator.css';

/**
 * UsageIndicator Component
 * Shows current usage limits and remaining quota for authenticated users
 * Displays upgrade prompts when limits are reached
 */
function UsageIndicator({ actionType, showUpgradePrompt = true }) {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [usageInfo, setUsageInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showLimitModal, setShowLimitModal] = useState(false);

  // Free tier limits for guest users
  const FREE_TIER_LIMITS = {
    section_analysis: { limit: 10, label: 'Section Analyses', period: 'per month' },
    memo_generation: { limit: 5, label: 'Memos', period: 'per month' },
    case_search: { limit: 3, label: 'Case Searches', period: 'per day' },
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchUsageInfo();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchUsageInfo = async () => {
    try {
      setLoading(true);
      const response = await api.get('/subscription/info');
      setUsageInfo(response.data);
    } catch (err) {
      console.error('Failed to fetch usage info:', err);
    } finally {
      setLoading(false);
    }
  };

  const getUsageForAction = () => {
    if (!usageInfo) return null;

    const { usage, limits } = usageInfo;

    switch (actionType) {
      case 'section_analysis':
        return {
          used: usage.section_analyses_used || 0,
          limit: limits.section_analyses_limit,
          label: 'Section Analyses',
          period: 'this month'
        };
      case 'memo_generation':
        return {
          used: usage.memo_generation_used || 0,
          limit: limits.memo_generation_limit,
          label: 'Memos',
          period: 'this month'
        };
      case 'case_search':
        return {
          used: usage.case_search_used || 0,
          limit: limits.case_search_limit,
          label: 'Case Searches',
          period: 'today'
        };
      default:
        return null;
    }
  };

  const calculatePercentage = (used, limit) => {
    if (limit === -1) return 0; // Unlimited
    return Math.min((used / limit) * 100, 100);
  };

  const isLimitReached = (used, limit) => {
    if (limit === -1) return false; // Unlimited
    return used >= limit;
  };

  const getStatusColor = (percentage) => {
    if (percentage >= 90) return '#dc3545'; // Red
    if (percentage >= 70) return '#ffc107'; // Yellow
    return '#28a745'; // Green
  };

  if (!isAuthenticated) {
    const guestLimit = FREE_TIER_LIMITS[actionType];
    if (!guestLimit) return null;

    return (
      <div className="usage-indicator guest-mode">
        <div className="usage-header">
          <div className="usage-label">
            <span className="label-icon">🔒</span>
            <span className="label-text">Free Tier Limit</span>
          </div>
          <div className="usage-count">
            {guestLimit.limit} {guestLimit.label}
            <span className="usage-period">{guestLimit.period}</span>
          </div>
        </div>
        <div className="guest-message">
          <span className="guest-icon">👋</span>
          <span>Sign up to track your usage and get started with {guestLimit.limit} {guestLimit.label.toLowerCase()} {guestLimit.period}!</span>
          <button className="btn-signup" onClick={() => navigate('/register')}>
            Sign Up Free
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="usage-indicator loading">Loading usage info...</div>;
  }

  const actionUsage = getUsageForAction();
  if (!actionUsage) return null;

  const { used, limit, label, period } = actionUsage;
  const percentage = calculatePercentage(used, limit);
  const limitReached = isLimitReached(used, limit);
  const statusColor = getStatusColor(percentage);

  return (
    <div className={`usage-indicator ${limitReached ? 'limit-reached' : ''}`}>
      <div className="usage-header">
        <div className="usage-label">
          <span className="label-icon">📊</span>
          <span className="label-text">{label}</span>
        </div>
        <div className="usage-count">
          {used} {limit === -1 ? '/ Unlimited' : `/ ${limit}`}
          <span className="usage-period">{period}</span>
        </div>
      </div>

      {limit !== -1 && (
        <div className="usage-progress-bar">
          <div
            className="usage-progress-fill"
            style={{
              width: `${percentage}%`,
              backgroundColor: statusColor
            }}
          />
        </div>
      )}

      {limitReached && showUpgradePrompt && (
        <div className="limit-warning">
          <span className="warning-icon">⚠️</span>
          <span className="warning-text">
            You've reached your {label.toLowerCase()} limit for {period}
          </span>
          <button
            className="btn-upgrade-small"
            onClick={() => navigate('/pricing')}
          >
            Upgrade Plan
          </button>
        </div>
      )}

      {!limitReached && limit !== -1 && percentage >= 70 && (
        <div className="limit-approaching">
          <span className="info-icon">ℹ️</span>
          <span className="info-text">
            {limit - used} {label.toLowerCase()} remaining {period}
          </span>
        </div>
      )}

      {limit === -1 && (
        <div className="unlimited-badge">
          <span className="unlimited-icon">∞</span>
          <span>Unlimited usage</span>
        </div>
      )}
    </div>
  );
}

export default UsageIndicator;
