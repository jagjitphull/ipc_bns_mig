import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/UserProfile.css';

function UserProfile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [usageStats, setUsageStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCancelModal, setShowCancelModal] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchSubscriptionData();
  }, [user, navigate]);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      const [subResponse, usageResponse] = await Promise.all([
        api.get('/subscription/info'),
        api.get('/subscription/usage')
      ]);
      setSubscriptionInfo(subResponse.data);
      setUsageStats(usageResponse.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = (tier) => {
    navigate('/pricing', { state: { selectedTier: tier } });
  };

  const handleCancelSubscription = async () => {
    try {
      await api.post('/subscription/cancel');
      setShowCancelModal(false);
      await fetchSubscriptionData();
      alert('Subscription cancelled. You can continue using until the end of your billing period.');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to cancel subscription');
    }
  };

  const calculatePercentage = (used, limit) => {
    if (limit === -1) return 0; // Unlimited
    return Math.min((used / limit) * 100, 100);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#28a745',
      trial: '#667eea',
      expired: '#dc3545',
      cancelled: '#ffc107'
    };
    return colors[status] || '#5a6c7d';
  };

  if (loading) {
    return <div className="loading">Loading your profile...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  const sub = subscriptionInfo?.subscription;
  const limits = subscriptionInfo?.limits;
  const usage = subscriptionInfo?.usage;

  return (
    <div className="user-profile">
      <div className="profile-header">
        <h2>Account & Subscription</h2>
        <p className="page-description">Manage your profile, subscription, and usage</p>
      </div>

      {/* User Information Card */}
      <div className="profile-card">
        <div className="card-header">
          <h3>👤 Profile Information</h3>
        </div>
        <div className="profile-details">
          <div className="detail-item">
            <label>Full Name</label>
            <span>{user.full_name || 'Not provided'}</span>
          </div>
          <div className="detail-item">
            <label>Email</label>
            <span>{user.email}</span>
          </div>
          <div className="detail-item">
            <label>Role</label>
            <span className="role-badge">{user.role?.toUpperCase() || 'USER'}</span>
          </div>
          <div className="detail-item">
            <label>Phone</label>
            <span>{user.phone || 'Not provided'}</span>
          </div>
          {user.bar_council_id && (
            <div className="detail-item">
              <label>Bar Council ID</label>
              <span>{user.bar_council_id}</span>
            </div>
          )}
          {user.organization && (
            <div className="detail-item">
              <label>Organization</label>
              <span>{user.organization}</span>
            </div>
          )}
        </div>
      </div>

      {/* Subscription Card */}
      <div className="profile-card subscription-card">
        <div className="card-header">
          <h3>💳 Subscription Details</h3>
          <span
            className="status-badge"
            style={{ backgroundColor: getStatusColor(sub?.status) }}
          >
            {sub?.status?.toUpperCase() || 'FREE'}
          </span>
        </div>

        <div className="subscription-details">
          <div className="sub-tier-display">
            <div className="tier-name">{sub?.tier?.toUpperCase() || 'FREE'} PLAN</div>
            <div className="tier-price">
              {sub?.tier === 'free' && '₹0/month'}
              {sub?.tier === 'professional' && '₹2,999/month'}
              {sub?.tier === 'enterprise' && '₹49,999/month'}
            </div>
          </div>

          <div className="sub-info-grid">
            {sub?.status === 'trial' && sub?.trial_ends_at && (
              <div className="info-item trial-info">
                <label>🎁 Trial Ends</label>
                <span className="highlight">{formatDate(sub.trial_ends_at)}</span>
              </div>
            )}

            {sub?.current_period_end && (
              <div className="info-item">
                <label>Next Billing Date</label>
                <span>{formatDate(sub.current_period_end)}</span>
              </div>
            )}

            <div className="info-item">
              <label>Member Since</label>
              <span>{formatDate(user.created_at)}</span>
            </div>

            {sub?.stripe_subscription_id && (
              <div className="info-item">
                <label>Subscription ID</label>
                <span className="mono">{sub.stripe_subscription_id.substring(0, 16)}...</span>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="subscription-actions">
            {sub?.tier === 'free' && (
              <button
                className="btn-primary btn-large"
                onClick={() => handleUpgrade('professional')}
              >
                ⬆️ Upgrade to Professional
              </button>
            )}

            {sub?.tier === 'professional' && (
              <>
                <button
                  className="btn-primary"
                  onClick={() => handleUpgrade('enterprise')}
                >
                  ⬆️ Upgrade to Enterprise
                </button>
                {sub?.status === 'active' && (
                  <button
                    className="btn-secondary btn-danger"
                    onClick={() => setShowCancelModal(true)}
                  >
                    Cancel Subscription
                  </button>
                )}
              </>
            )}

            {sub?.status === 'cancelled' && (
              <button
                className="btn-primary"
                onClick={() => handleUpgrade(sub.tier)}
              >
                Reactivate Subscription
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Usage Statistics */}
      <div className="profile-card usage-card">
        <div className="card-header">
          <h3>📊 Usage Statistics</h3>
          <span className="usage-period">Current Billing Period</span>
        </div>

        <div className="usage-stats">
          {/* Section Analyses */}
          <div className="usage-item">
            <div className="usage-header">
              <label>Section Analyses</label>
              <span className="usage-count">
                {usage?.section_analyses_used || 0}
                {limits?.section_analyses_limit === -1
                  ? ' / Unlimited'
                  : ` / ${limits?.section_analyses_limit || 0}`}
              </span>
            </div>
            {limits?.section_analyses_limit !== -1 && (
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${calculatePercentage(
                      usage?.section_analyses_used || 0,
                      limits?.section_analyses_limit || 1
                    )}%`
                  }}
                />
              </div>
            )}
          </div>

          {/* Memo Generation */}
          <div className="usage-item">
            <div className="usage-header">
              <label>Memos Generated</label>
              <span className="usage-count">
                {usage?.memo_generation_used || 0}
                {limits?.memo_generation_limit === -1
                  ? ' / Unlimited'
                  : ` / ${limits?.memo_generation_limit || 0}`}
              </span>
            </div>
            {limits?.memo_generation_limit !== -1 && (
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${calculatePercentage(
                      usage?.memo_generation_used || 0,
                      limits?.memo_generation_limit || 1
                    )}%`
                  }}
                />
              </div>
            )}
          </div>

          {/* Case Searches */}
          <div className="usage-item">
            <div className="usage-header">
              <label>Case Searches (Today)</label>
              <span className="usage-count">
                {usage?.case_search_used || 0}
                {limits?.case_search_daily_limit === -1
                  ? ' / Unlimited'
                  : ` / ${limits?.case_search_daily_limit || 0}`}
              </span>
            </div>
            {limits?.case_search_daily_limit !== -1 && (
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${calculatePercentage(
                      usage?.case_search_used || 0,
                      limits?.case_search_daily_limit || 1
                    )}%`
                  }}
                />
              </div>
            )}
          </div>

          {/* API Calls */}
          {sub?.tier !== 'free' && (
            <div className="usage-item">
              <div className="usage-header">
                <label>API Calls (Today)</label>
                <span className="usage-count">
                  {usage?.api_calls_used || 0}
                  {limits?.api_calls_daily_limit === -1
                    ? ' / Unlimited'
                    : ` / ${limits?.api_calls_daily_limit || 0}`}
                </span>
              </div>
              {limits?.api_calls_daily_limit !== -1 && (
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${calculatePercentage(
                        usage?.api_calls_used || 0,
                        limits?.api_calls_daily_limit || 1
                      )}%`
                    }}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Usage Chart */}
        {usageStats?.daily_usage && usageStats.daily_usage.length > 0 && (
          <div className="usage-chart">
            <h4>Last 30 Days Activity</h4>
            <div className="chart-container">
              {usageStats.daily_usage.map((day, index) => (
                <div key={index} className="chart-bar">
                  <div
                    className="bar-fill"
                    style={{
                      height: `${Math.min((day.count / Math.max(...usageStats.daily_usage.map(d => d.count))) * 100, 100)}%`
                    }}
                    title={`${day.date}: ${day.count} actions`}
                  />
                  {index % 5 === 0 && (
                    <span className="bar-label">{new Date(day.date).getDate()}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Features by Tier */}
      <div className="profile-card features-card">
        <div className="card-header">
          <h3>✨ Your Plan Features</h3>
        </div>
        <div className="features-list">
          {limits?.section_analyses_limit === -1 ? (
            <div className="feature-item">✅ Unlimited Section Analyses</div>
          ) : (
            <div className="feature-item">
              📊 {limits?.section_analyses_limit} Section Analyses/month
            </div>
          )}

          {limits?.memo_generation_limit === -1 ? (
            <div className="feature-item">✅ Unlimited Memo Generation</div>
          ) : (
            <div className="feature-item">
              📝 {limits?.memo_generation_limit} Memos/month
            </div>
          )}

          {limits?.case_search_daily_limit === -1 ? (
            <div className="feature-item">✅ Unlimited Case Search</div>
          ) : (
            <div className="feature-item">
              🔍 {limits?.case_search_daily_limit} Case Searches/day
            </div>
          )}

          {sub?.tier !== 'free' ? (
            <div className="feature-item">✅ API Access</div>
          ) : (
            <div className="feature-item disabled">❌ No API Access</div>
          )}

          {sub?.tier === 'enterprise' && (
            <>
              <div className="feature-item">✅ Team Collaboration</div>
              <div className="feature-item">✅ White-label Options</div>
              <div className="feature-item">✅ Priority Support</div>
            </>
          )}
        </div>
      </div>

      {/* Cancel Subscription Modal */}
      {showCancelModal && (
        <div className="modal-overlay" onClick={() => setShowCancelModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Cancel Subscription?</h3>
            <p>Are you sure you want to cancel your subscription? You'll continue to have access until the end of your billing period.</p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowCancelModal(false)}>
                Keep Subscription
              </button>
              <button className="btn-primary btn-danger" onClick={handleCancelSubscription}>
                Yes, Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserProfile;
