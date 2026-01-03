import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import '../styles/Pricing.css';

function Pricing() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [selectedTier, setSelectedTier] = useState(location.state?.selectedTier || null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await api.get('/subscription/plans');
      setPlans(response.data.plans || []);
    } catch (err) {
      console.error('Failed to fetch plans:', err);
      // Fallback to hardcoded plans
      setPlans([
        {
          tier: 'free',
          name: 'Free',
          price: 0,
          currency: 'INR',
          billing_period: 'month',
          features: [
            '10 Section Analyses per month',
            '5 Memos per month',
            '3 Case Searches per day',
            'Basic support',
            'No API access'
          ],
          limits: {
            section_analyses_limit: 10,
            memo_generation_limit: 5,
            case_search_daily_limit: 3,
            api_calls_daily_limit: 0
          }
        },
        {
          tier: 'professional',
          name: 'Professional',
          price: 2999,
          currency: 'INR',
          billing_period: 'month',
          features: [
            'Unlimited Section Analyses',
            '50 Memos per month',
            'Unlimited Case Searches',
            'API access (100 calls/day)',
            'Priority email support',
            '14-day free trial'
          ],
          limits: {
            section_analyses_limit: -1,
            memo_generation_limit: 50,
            case_search_daily_limit: -1,
            api_calls_daily_limit: 100
          },
          recommended: true
        },
        {
          tier: 'enterprise',
          name: 'Enterprise',
          price: 49999,
          currency: 'INR',
          billing_period: 'month',
          features: [
            'Everything in Professional',
            'Unlimited Memos',
            'Unlimited API access',
            'Team collaboration (25 users)',
            'White-label options',
            'Dedicated account manager',
            'Custom integrations',
            '24/7 priority support'
          ],
          limits: {
            section_analyses_limit: -1,
            memo_generation_limit: -1,
            case_search_daily_limit: -1,
            api_calls_daily_limit: -1
          }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (tier) => {
    if (!isAuthenticated) {
      navigate('/register', { state: { selectedTier: tier } });
      return;
    }

    if (tier === 'free') {
      alert('You are already on the free plan!');
      return;
    }

    try {
      setProcessing(true);
      setSelectedTier(tier);

      // Call upgrade endpoint
      const response = await api.post('/subscription/upgrade', {
        new_tier: tier
      });

      if (response.data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = response.data.checkout_url;
      } else if (response.data.message) {
        alert(response.data.message);
        navigate('/profile');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to process subscription';
      alert(errorMsg);

      // If Stripe is not configured, show mock success
      if (errorMsg.includes('Stripe') || errorMsg.includes('not configured')) {
        const confirmed = window.confirm(
          `Stripe is not configured yet. Would you like to simulate upgrading to ${tier.toUpperCase()}?\n\n` +
          `This is a demo mode - no actual payment will be processed.`
        );

        if (confirmed) {
          alert(`Demo: Subscription upgraded to ${tier.toUpperCase()}! (No payment processed)`);
          navigate('/profile');
        }
      }
    } finally {
      setProcessing(false);
      setSelectedTier(null);
    }
  };

  const formatPrice = (price, currency) => {
    if (price === 0) return 'Free';
    return `₹${price.toLocaleString('en-IN')}`;
  };

  const getCurrentTier = () => {
    return user?.subscription_tier || 'free';
  };

  const isCurrentPlan = (tier) => {
    return isAuthenticated && getCurrentTier() === tier;
  };

  const canUpgrade = (tier) => {
    if (!isAuthenticated) return true;
    const current = getCurrentTier();
    const tierOrder = { free: 0, professional: 1, enterprise: 2 };
    return tierOrder[tier] > tierOrder[current];
  };

  if (loading) {
    return <div className="loading">Loading pricing plans...</div>;
  }

  return (
    <div className="pricing-page">
      <div className="pricing-header">
        <h2>Choose Your Plan</h2>
        <p className="page-description">
          Select the perfect plan for your legal research needs
        </p>
        {!isAuthenticated && (
          <div className="trial-notice">
            🎁 Start with a 14-day free trial of Professional - No credit card required!
          </div>
        )}
      </div>

      <div className="pricing-grid">
        {plans.map((plan) => (
          <div
            key={plan.tier}
            className={`pricing-card ${plan.recommended ? 'recommended' : ''} ${
              isCurrentPlan(plan.tier) ? 'current-plan' : ''
            }`}
          >
            {plan.recommended && <div className="recommended-badge">Most Popular</div>}
            {isCurrentPlan(plan.tier) && <div className="current-badge">Current Plan</div>}

            <div className="plan-header">
              <h3 className="plan-name">{plan.name}</h3>
              <div className="plan-price">
                <span className="price-amount">{formatPrice(plan.price, plan.currency)}</span>
                {plan.price > 0 && <span className="price-period">/month</span>}
              </div>
            </div>

            <div className="plan-features">
              {plan.features.map((feature, index) => (
                <div key={index} className="feature-item">
                  <span className="feature-icon">✓</span>
                  <span className="feature-text">{feature}</span>
                </div>
              ))}
            </div>

            <div className="plan-action">
              {isCurrentPlan(plan.tier) ? (
                <button className="btn-current" disabled>
                  Current Plan
                </button>
              ) : canUpgrade(plan.tier) ? (
                <button
                  className={`btn-subscribe ${plan.recommended ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => handleSubscribe(plan.tier)}
                  disabled={processing && selectedTier === plan.tier}
                >
                  {processing && selectedTier === plan.tier ? (
                    'Processing...'
                  ) : plan.tier === 'free' ? (
                    'Get Started'
                  ) : isAuthenticated ? (
                    `Upgrade to ${plan.name}`
                  ) : (
                    `Start Free Trial`
                  )}
                </button>
              ) : (
                <button className="btn-downgrade" onClick={() => navigate('/profile')}>
                  Manage Subscription
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Table */}
      <div className="comparison-section">
        <h3>Feature Comparison</h3>
        <div className="comparison-table">
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                {plans.map((plan) => (
                  <th key={plan.tier}>{plan.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Section Analyses</td>
                {plans.map((plan) => (
                  <td key={plan.tier}>
                    {plan.limits.section_analyses_limit === -1
                      ? '∞ Unlimited'
                      : `${plan.limits.section_analyses_limit}/month`}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Memo Generation</td>
                {plans.map((plan) => (
                  <td key={plan.tier}>
                    {plan.limits.memo_generation_limit === -1
                      ? '∞ Unlimited'
                      : `${plan.limits.memo_generation_limit}/month`}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Case Searches</td>
                {plans.map((plan) => (
                  <td key={plan.tier}>
                    {plan.limits.case_search_daily_limit === -1
                      ? '∞ Unlimited'
                      : `${plan.limits.case_search_daily_limit}/day`}
                  </td>
                ))}
              </tr>
              <tr>
                <td>API Access</td>
                {plans.map((plan) => (
                  <td key={plan.tier}>
                    {plan.limits.api_calls_daily_limit === 0
                      ? '❌'
                      : plan.limits.api_calls_daily_limit === -1
                      ? '✓ Unlimited'
                      : `${plan.limits.api_calls_daily_limit}/day`}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Support</td>
                <td>Email</td>
                <td>Priority Email</td>
                <td>24/7 Dedicated</td>
              </tr>
              <tr>
                <td>Team Collaboration</td>
                <td>❌</td>
                <td>❌</td>
                <td>✓ 25 users</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="faq-section">
        <h3>Frequently Asked Questions</h3>
        <div className="faq-grid">
          <div className="faq-item">
            <h4>How does the free trial work?</h4>
            <p>
              Sign up for Professional and get 14 days of full access - no credit card required.
              You can cancel anytime before the trial ends.
            </p>
          </div>
          <div className="faq-item">
            <h4>Can I change plans later?</h4>
            <p>
              Yes! You can upgrade or downgrade your plan at any time from your account settings.
              Changes take effect immediately.
            </p>
          </div>
          <div className="faq-item">
            <h4>What payment methods do you accept?</h4>
            <p>
              We accept all major credit cards, debit cards, UPI, and net banking through our
              secure Stripe payment gateway.
            </p>
          </div>
          <div className="faq-item">
            <h4>Is my data secure?</h4>
            <p>
              Absolutely. All data is encrypted in transit and at rest. We follow industry best
              practices for data security and privacy.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      {!isAuthenticated && (
        <div className="cta-section">
          <h3>Ready to Get Started?</h3>
          <p>Join hundreds of legal professionals using our AI-powered legal research platform</p>
          <button className="btn-primary btn-large" onClick={() => navigate('/register')}>
            Start Free Trial
          </button>
        </div>
      )}
    </div>
  );
}

export default Pricing;
