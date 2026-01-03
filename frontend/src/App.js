import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Dashboard from './pages/Dashboard';
import SectionAnalyzer from './pages/SectionAnalyzer';
import MemoGenerator from './pages/MemoGenerator';
import CaseSearch from './pages/CaseSearch';
import Login from './pages/Login';
import Register from './pages/Register';
import './styles/App.css';
import './styles/Auth.css';

// Navbar component with authentication support
function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <h1>IPC/BNS Legal Reasoning Agent</h1>
          <p className="nav-subtitle">Statute Migrator with RAG + Reasoning</p>
        </div>
        <div className="nav-links">
          <Link to="/" className="nav-link">Dashboard</Link>
          <Link to="/analyze" className="nav-link">Section Analyzer</Link>
          <Link to="/memo" className="nav-link">Memo Generator</Link>
          <Link to="/cases" className="nav-link">Case Search</Link>

          {isAuthenticated ? (
            <div className="user-menu">
              <span className="user-greeting">
                👤 {user?.full_name || user?.email}
              </span>
              <span className="subscription-badge">
                {user?.subscription_tier?.toUpperCase() || 'FREE'}
              </span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="btn-primary btn-small">
                Sign Up Free
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

// Main App component
function AppContent() {
  return (
    <div className="App">
      <Navbar />

      <div className="main-content">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Main application routes - accessible to all (backend has optional auth) */}
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyze" element={<SectionAnalyzer />} />
          <Route path="/memo" element={<MemoGenerator />} />
          <Route path="/cases" element={<CaseSearch />} />
        </Routes>
      </div>

      <footer className="footer">
        <p>IPC/BNS Legal Reasoning Agent v2.0 | AI-Powered Legal Analysis System</p>
        <p className="disclaimer">
          ⚠️ This system provides automated legal analysis. Always consult qualified legal professionals.
        </p>
      </footer>
    </div>
  );
}

// Root App component with providers
function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
