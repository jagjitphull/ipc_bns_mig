import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const navigate = useNavigate();
  const { login, error: authError } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData);
      navigate('/'); // Redirect to dashboard after login
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Welcome Back</h2>
          <p>Login to your IPC/BNS Legal Platform account</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {(error || authError) && (
            <div className="error-message">
              {error || authError}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="lawyer@example.com"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>

          <div className="form-options">
            <label className="checkbox-label">
              <input type="checkbox" />
              <span>Remember me</span>
            </label>
            <Link to="/forgot-password" className="link-text">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            className="btn-primary btn-large btn-block"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>

          <div className="auth-footer">
            <p>
              Don't have an account?{' '}
              <Link to="/register" className="link-primary">
                Register now
              </Link>
            </p>
            <p className="trial-notice">
              ✨ Get 14 days free trial on Professional plan!
            </p>
          </div>
        </form>
      </div>

      <div className="auth-features">
        <h3>Why Choose Our Platform?</h3>
        <div className="feature-list">
          <div className="feature-item">
            <span className="feature-icon">⚖️</span>
            <div>
              <h4>Complete IPC↔BNS Coverage</h4>
              <p>21+ sections with detailed analysis and landmark cases</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <div>
              <h4>AI-Powered Legal Analysis</h4>
              <p>RAG-based case law search and reasoning</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📝</span>
            <div>
              <h4>Professional Memos</h4>
              <p>Generate lawyer-style documents instantly</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
