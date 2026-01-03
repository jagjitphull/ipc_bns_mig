import React, { useState } from 'react';
import { apiService } from '../services/api';
import UsageIndicator from '../components/UsageIndicator';

function CaseSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search cases');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const parseMetadata = (metadata) => {
    try {
      return {
        case_name: metadata.case_name || 'Unknown Case',
        citation: metadata.citation || 'N/A',
        court: metadata.court || 'N/A',
        year: metadata.year || 'N/A',
        validity_status: metadata.validity_status || 'unknown'
      };
    } catch {
      return null;
    }
  };

  return (
    <div className="case-search">
      <h2>Case Law Search</h2>
      <p className="page-description">
        Semantic search over landmark cases using RAG (Retrieval Augmented Generation).
        Search by facts, legal issues, or legal principles.
      </p>

      <UsageIndicator actionType="case_search" />

      <form onSubmit={handleSearch} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 'murder with provocation', 'sedition free speech', 'theft dishonest intention'"
            className="search-input"
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Searching...' : 'Search Cases'}
          </button>
        </div>
      </form>

      <div className="search-examples">
        <strong>Example queries:</strong>
        <ul>
          <li>"What is grave and sudden provocation in murder cases?"</li>
          <li>"Cases on sedition and freedom of speech"</li>
          <li>"Dishonest intention requirement for theft"</li>
          <li>"Difference between murder and culpable homicide"</li>
        </ul>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {results && (
        <div className="search-results">
          <div className="results-header">
            <h3>Search Results</h3>
            <span className="results-count">
              Found {results.results?.length || 0} relevant cases
            </span>
          </div>

          {results.results?.length === 0 && (
            <div className="no-results">
              No cases found matching your query. Try different keywords.
            </div>
          )}

          <div className="results-list">
            {results.results?.map((result, idx) => {
              const metadata = parseMetadata(result.metadata);
              if (!metadata) return null;

              return (
                <div key={idx} className="result-card">
                  <div className="result-header">
                    <div>
                      <h4>{metadata.case_name}</h4>
                      <div className="case-meta">
                        <span>{metadata.citation}</span>
                        <span>{metadata.court}</span>
                        <span>{metadata.year}</span>
                      </div>
                    </div>
                    <div className={`validity-badge validity-${metadata.validity_status}`}>
                      {metadata.validity_status.replace('_', ' ')}
                    </div>
                  </div>

                  <div className="result-content">
                    <div className="relevance-score">
                      Relevance: {result.distance ? (100 - result.distance * 100).toFixed(1) : 'N/A'}%
                    </div>
                    <div className="case-excerpt">
                      {result.document?.substring(0, 500)}...
                    </div>
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
