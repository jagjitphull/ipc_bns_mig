import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import SectionAnalyzer from './pages/SectionAnalyzer';
import MemoGenerator from './pages/MemoGenerator';
import CaseSearch from './pages/CaseSearch';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
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
            </div>
          </div>
        </nav>

        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<SectionAnalyzer />} />
            <Route path="/memo" element={<MemoGenerator />} />
            <Route path="/cases" element={<CaseSearch />} />
          </Routes>
        </div>

        <footer className="footer">
          <p>IPC/BNS Legal Reasoning Agent v1.0 | AI-Powered Legal Analysis System</p>
          <p className="disclaimer">
            ⚠️ This system provides automated legal analysis. Always consult qualified legal professionals.
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
