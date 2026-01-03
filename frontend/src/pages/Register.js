import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Register() {
  const navigate = useNavigate();
  const { register, error: authError } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    phone: '',
    bar_council_id: '',
    organization: '',
    role: 'lawyer'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordErrors, setPasswordErrors] = useState([]);

  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push('At least 8 characters long');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('At least one uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('At least one lowercase letter');
    }
    if (!/[0-9]/.test(password)) {
      errors.push('At least one digit');
    }
    return errors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Validate password on change
    if (name === 'password') {
      setPasswordErrors(validatePassword(value));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    const errors = validatePassword(formData.password);
    if (errors.length > 0) {
      setError('Password does not meet requirements');
      return;
    }

    setLoading(true);

    try {
      // Remove confirmPassword before sending
      const { confirmPassword, ...registerData } = formData;
      await register(registerData);
      navigate('/'); // Redirect to dashboard after registration
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card register-card">
        <div className="auth-header">
          <h2>Create Your Account</h2>
          <p>Start your 14-day free trial on Professional plan</p>
          <div className="trial-badge">
            🎉 No credit card required for trial
          </div>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {(error || authError) && (
            <div className="error-message">
              {error || authError}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="full_name">Full Name *</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="Advocate John Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="lawyer@example.com"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="form-input"
                placeholder="+91 98765 43210"
              />
            </div>

            <div className="form-group">
              <label htmlFor="bar_council_id">Bar Council ID</label>
              <input
                type="text"
                id="bar_council_id"
                name="bar_council_id"
                value={formData.bar_council_id}
                onChange={handleChange}
                className="form-input"
                placeholder="D/12345/2020"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="organization">Organization/Firm</label>
              <input
                type="text"
                id="organization"
                name="organization"
                value={formData.organization}
                onChange={handleChange}
                className="form-input"
                placeholder="Law Firm Name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="role">Role *</label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                required
                className="form-input"
              >
                <option value="lawyer">Lawyer</option>
                <option value="researcher">Legal Researcher</option>
                <option value="student">Law Student</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="••••••••"
              />
              {passwordErrors.length > 0 && formData.password && (
                <div className="password-requirements">
                  <p>Password must have:</p>
                  <ul>
                    {passwordErrors.map((err, idx) => (
                      <li key={idx} className="requirement-error">✗ {err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" required />
              <span>
                I agree to the{' '}
                <Link to="/terms" className="link-text">Terms of Service</Link>
                {' '}and{' '}
                <Link to="/privacy" className="link-text">Privacy Policy</Link>
              </span>
            </label>
          </div>

          <button
            type="submit"
            className="btn-primary btn-large btn-block"
            disabled={loading || passwordErrors.length > 0}
          >
            {loading ? 'Creating Account...' : 'Start Free Trial'}
          </button>

          <div className="auth-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="link-primary">
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>

      <div className="subscription-preview">
        <h3>What's Included in Your Trial</h3>
        <div className="plan-features">
          <div className="plan-feature">
            <span className="check-icon">✓</span>
            <span>Unlimited section analyses</span>
          </div>
          <div className="plan-feature">
            <span className="check-icon">✓</span>
            <span>50 memo generations per month</span>
          </div>
          <div className="plan-feature">
            <span className="check-icon">✓</span>
            <span>Unlimited case law searches</span>
          </div>
          <div className="plan-feature">
            <span className="check-icon">✓</span>
            <span>API access (100 calls/day)</span>
          </div>
          <div className="plan-feature">
            <span className="check-icon">✓</span>
            <span>Save and organize research</span>
          </div>
          <div className="plan-feature">
            <span className="check-icon">✓</span>
            <span>Export without watermarks</span>
          </div>
        </div>
        <p className="pricing-info">
          After trial: ₹2,999/month or cancel anytime
        </p>
      </div>
    </div>
  );
}

export default Register;
