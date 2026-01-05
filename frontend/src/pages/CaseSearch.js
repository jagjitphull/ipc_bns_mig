import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import UsageIndicator from '../components/UsageIndicator';

// Popular landmark cases for quick access
const LANDMARK_CASES = [
  { name: 'Bachan Singh', section: '302', topic: 'Death penalty - Rarest of rare' },
  { name: 'Navtej Singh Johar', section: '377', topic: 'Section 377 decriminalization' },
  { name: 'D.K. Basu', section: 'Arrest', topic: '11 Custodial rights guidelines' },
  { name: 'Vishaka', section: '354', topic: 'Sexual harassment guidelines' },
  { name: 'Arnesh Kumar', section: '498A', topic: 'Arrest guidelines' },
  { name: 'Lalita Kumari', section: 'FIR', topic: 'Mandatory FIR registration' },
];

function CaseSearch() {
  const navigate = useNavigate();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Advanced filters
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    year: '',
    yearFrom: '',
    yearTo: '',
    court: '',
    section: '',
    validityStatus: ''
  });
  const [searchMode, setSearchMode] = useState('semantic'); // semantic, exact, section

  // Show loading spinner while auth is initializing
  if (authLoading) {
    return (
      <div className="case-search">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="case-search">
        <h2>Case Law Search</h2>
        <p className="page-description">
          Search through 51+ landmark cases with advanced filters.
        </p>

        <div className="auth-required">
          <div className="auth-required-icon">🔒</div>
          <h3>Authentication Required</h3>
          <p>Please log in to search case law and access advanced features.</p>
          <div className="auth-actions">
            <button
              className="btn-primary"
              onClick={() => navigate('/login')}
            >
              Log In
            </button>
            <button
              className="btn-secondary"
              onClick={() => navigate('/register')}
            >
              Sign Up Free - 14 Day Trial
            </button>
          </div>
        </div>

        {/* Show popular cases as preview */}
        <div className="popular-cases">
          <h3>🏛️ Popular Landmark Cases (Preview)</h3>
          <div className="case-chips">
            {LANDMARK_CASES.map((lcase, idx) => (
              <div
                key={idx}
                className="case-chip disabled"
                title="Login required"
              >
                <span className="chip-name">{lcase.name}</span>
                <span className="chip-section">§ {lcase.section}</span>
                <span className="chip-topic">{lcase.topic}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await apiService.searchCases(query, 10);

      // Apply client-side filters
      let filteredResults = response.data.results || [];

      if (filters.yearFrom || filters.yearTo) {
        filteredResults = filteredResults.filter(result => {
          const year = result.metadata?.year;
          if (!year) return true;
          const from = filters.yearFrom ? parseInt(filters.yearFrom) : 0;
          const to = filters.yearTo ? parseInt(filters.yearTo) : 9999;
          return year >= from && year <= to;
        });
      }

      if (filters.court) {
        filteredResults = filteredResults.filter(result =>
          result.metadata?.court?.toLowerCase().includes(filters.court.toLowerCase())
        );
      }

      if (filters.section) {
        filteredResults = filteredResults.filter(result =>
          result.metadata?.ipc_sections?.some(sec =>
            sec.toLowerCase().includes(filters.section.toLowerCase())
          )
        );
      }

      if (filters.validityStatus) {
        filteredResults = filteredResults.filter(result =>
          result.metadata?.validity_status === filters.validityStatus
        );
      }

      setResults({
        ...response.data,
        results: filteredResults,
        totalResults: response.data.results?.length || 0,
        filteredCount: filteredResults.length
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search cases');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSearch = (caseName) => {
    setQuery(caseName);
    setTimeout(() => {
      const form = document.querySelector('.search-form');
      if (form) form.requestSubmit();
    }, 100);
  };

  const parseMetadata = (metadata) => {
    try {
      // Handle ipc_sections - could be array, string, or undefined
      let ipcSections = [];
      if (metadata.ipc_sections) {
        if (Array.isArray(metadata.ipc_sections)) {
          ipcSections = metadata.ipc_sections;
        } else if (typeof metadata.ipc_sections === 'string') {
          // Split comma-separated string into array
          ipcSections = metadata.ipc_sections.split(',').map(s => s.trim()).filter(s => s);
        }
      }

      return {
        case_name: metadata.case_name || 'Unknown Case',
        citation: metadata.citation || 'N/A',
        court: metadata.court || 'N/A',
        year: metadata.year || 'N/A',
        validity_status: metadata.validity_status || 'unknown',
        ipc_sections: ipcSections
      };
    } catch {
      return null;
    }
  };

  const clearFilters = () => {
    setFilters({
      year: '',
      yearFrom: '',
      yearTo: '',
      court: '',
      section: '',
      validityStatus: ''
    });
  };

  const activeFilterCount = Object.values(filters).filter(v => v).length;

  return (
    <div className="case-search">
      <h2>Case Law Search</h2>
      <p className="page-description">
        Search through 51+ landmark cases with advanced filters.
        Use semantic search, exact case names, or filter by section/year/court.
      </p>

      <UsageIndicator actionType="case_search" />

      <form onSubmit={handleSearch} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by case name, legal principle, or keywords..."
            className="search-input"
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Searching...' : 'Search Cases'}
          </button>
        </div>

        {/* Advanced Filters Toggle */}
        <div className="filter-controls">
          <button
            type="button"
            className="btn-secondary btn-small"
            onClick={() => setShowFilters(!showFilters)}
          >
            🔍 {showFilters ? 'Hide' : 'Show'} Advanced Filters
            {activeFilterCount > 0 && <span className="filter-badge">{activeFilterCount}</span>}
          </button>
          {activeFilterCount > 0 && (
            <button
              type="button"
              className="btn-link"
              onClick={clearFilters}
            >
              Clear all filters
            </button>
          )}
        </div>

        {/* Advanced Filters Panel */}
        {showFilters && (
          <div className="advanced-filters">
            <div className="filter-grid">
              <div className="filter-group">
                <label>Year Range:</label>
                <div className="year-range">
                  <input
                    type="number"
                    placeholder="From (e.g., 1980)"
                    value={filters.yearFrom}
                    onChange={(e) => setFilters({...filters, yearFrom: e.target.value})}
                    min="1900"
                    max="2030"
                  />
                  <span>to</span>
                  <input
                    type="number"
                    placeholder="To (e.g., 2024)"
                    value={filters.yearTo}
                    onChange={(e) => setFilters({...filters, yearTo: e.target.value})}
                    min="1900"
                    max="2030"
                  />
                </div>
              </div>

              <div className="filter-group">
                <label>Court:</label>
                <select
                  value={filters.court}
                  onChange={(e) => setFilters({...filters, court: e.target.value})}
                >
                  <option value="">All Courts</option>
                  <option value="Supreme Court">Supreme Court</option>
                  <option value="High Court">High Courts</option>
                  <option value="Constitution Bench">Constitution Bench</option>
                </select>
              </div>

              <div className="filter-group">
                <label>IPC Section:</label>
                <input
                  type="text"
                  placeholder="e.g., 302, 376, 498A"
                  value={filters.section}
                  onChange={(e) => setFilters({...filters, section: e.target.value})}
                />
              </div>

              <div className="filter-group">
                <label>Validity Status:</label>
                <select
                  value={filters.validityStatus}
                  onChange={(e) => setFilters({...filters, validityStatus: e.target.value})}
                >
                  <option value="">All Statuses</option>
                  <option value="valid">Valid</option>
                  <option value="requires_review">Requires Review</option>
                  <option value="superseded">Superseded</option>
                  <option value="affirmed_expanded">Affirmed & Expanded</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </form>

      {/* Popular Landmark Cases */}
      {!results && !loading && (
        <div className="popular-cases">
          <h3>🏛️ Popular Landmark Cases</h3>
          <div className="case-chips">
            {LANDMARK_CASES.map((lcase, idx) => (
              <button
                key={idx}
                className="case-chip"
                onClick={() => handleQuickSearch(lcase.name)}
                title={lcase.topic}
              >
                <span className="chip-name">{lcase.name}</span>
                <span className="chip-section">§ {lcase.section}</span>
                <span className="chip-topic">{lcase.topic}</span>
              </button>
            ))}
          </div>
          <div className="help-text">
            💡 <strong>Tip:</strong> Click any case above for instant search, or use advanced filters for precise results.
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {results && (
        <div className="search-results">
          <div className="results-header">
            <h3>Search Results</h3>
            <div className="results-info">
              {results.filteredCount !== results.totalResults ? (
                <span className="results-count">
                  Showing {results.filteredCount} of {results.totalResults} cases
                  {activeFilterCount > 0 && <span className="filtered-indicator"> (filtered)</span>}
                </span>
              ) : (
                <span className="results-count">
                  Found {results.results?.length || 0} relevant cases
                </span>
              )}
            </div>
          </div>

          {results.results?.length === 0 && (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <h4>No cases found</h4>
              <p>Try adjusting your search query or filters.</p>
              {activeFilterCount > 0 && (
                <button className="btn-secondary" onClick={clearFilters}>
                  Clear Filters
                </button>
              )}
            </div>
          )}

          <div className="results-list">
            {results.results?.map((result, idx) => {
              const metadata = parseMetadata(result.metadata);
              if (!metadata) return null;

              return (
                <div key={idx} className="result-card enhanced">
                  <div className="result-rank">#{idx + 1}</div>

                  <div className="result-header">
                    <div className="header-main">
                      <h4>{metadata.case_name}</h4>
                      <div className="case-meta">
                        <span className="citation">📄 {metadata.citation}</span>
                        <span className="court">🏛️ {metadata.court}</span>
                        <span className="year">📅 {metadata.year}</span>
                      </div>
                    </div>
                    <div className="header-badges">
                      <div className={`validity-badge validity-${metadata.validity_status}`}>
                        {metadata.validity_status.replace('_', ' ').toUpperCase()}
                      </div>
                      <div className="relevance-score">
                        {result.distance ? (100 - result.distance * 100).toFixed(0) : 'N/A'}% Match
                      </div>
                    </div>
                  </div>

                  {metadata.ipc_sections && metadata.ipc_sections.length > 0 && (
                    <div className="related-sections">
                      <strong>Related IPC Sections:</strong>
                      {metadata.ipc_sections.map((sec, i) => (
                        <span key={i} className="section-tag">§ {sec}</span>
                      ))}
                    </div>
                  )}

                  <div className="result-content">
                    <div className="case-excerpt">
                      {result.document?.substring(0, 400)}...
                    </div>
                    <button className="btn-link read-more">
                      Read full case details →
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default CaseSearch;
