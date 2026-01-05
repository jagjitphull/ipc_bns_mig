import React, { useState } from 'react';
import { apiService } from '../services/api';
import UsageIndicator from '../components/UsageIndicator';

function MemoGenerator() {
  const [sections, setSections] = useState('');
  const [context, setContext] = useState('');
  const [memo, setMemo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!sections.trim()) {
      setError('Please enter at least one IPC section');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Parse sections (comma or space separated)
      const sectionList = sections
        .split(/[,\s]+/)
        .map(s => s.trim())
        .filter(s => s);

      const response = await apiService.generateMemo(sectionList, context);
      setMemo(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate memo');
      setMemo(null);
    } finally {
      setLoading(false);
    }
  };

  const downloadMemo = () => {
    if (!memo) return;

    const element = document.createElement('a');
    const file = new Blob([memo.memo], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `legal_memo_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadMemoPDF = async () => {
    if (!memo || !sections) return;

    try {
      setLoading(true);

      // Parse sections
      const sectionList = sections
        .split(/[,\s]+/)
        .map(s => s.trim())
        .filter(s => s);

      // Call PDF endpoint
      const response = await apiService.generateMemoPDF(sectionList, context);

      // Create blob from response
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      // Download
      const element = document.createElement('a');
      element.href = url;
      element.download = `Legal_Memo_${sectionList[0]}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

      // Cleanup
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate PDF');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!memo) return;

    navigator.clipboard.writeText(memo.memo).then(() => {
      alert('Memo copied to clipboard!');
    });
  };

  return (
    <div className="memo-generator">
      <h2>Legal Memorandum Generator</h2>
      <p className="page-description">
        Generate comprehensive lawyer-style memoranda analyzing IPC to BNS transitions
        with validity warnings and recommendations.
      </p>

      <UsageIndicator actionType="memo_generation" />

      <form onSubmit={handleGenerate} className="memo-form">
        <div className="form-group">
          <label htmlFor="sections">IPC Sections</label>
          <input
            id="sections"
            type="text"
            value={sections}
            onChange={(e) => setSections(e.target.value)}
            placeholder="e.g., 302, 304A, 420 (comma or space separated)"
            className="form-input"
          />
          <small>Enter multiple sections separated by commas or spaces</small>
        </div>

        <div className="form-group">
          <label htmlFor="context">Query Context (Optional)</label>
          <textarea
            id="context"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Provide context for the legal query (e.g., 'Client charged under Section 302 IPC for murder case')"
            className="form-textarea"
            rows="4"
          />
        </div>

        <button type="submit" className="btn-primary btn-large" disabled={loading}>
          {loading ? 'Generating Memorandum...' : 'Generate Memorandum'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {memo && (
        <div className="memo-results">
          <div className="memo-header">
            <h3>Generated Memorandum</h3>
            <div className="memo-actions">
              <button onClick={copyToClipboard} className="btn-secondary">
                📋 Copy
              </button>
              <button onClick={downloadMemo} className="btn-secondary">
                📄 Download TXT
              </button>
              <button onClick={downloadMemoPDF} className="btn-primary" disabled={loading}>
                📑 Download PDF
              </button>
            </div>
          </div>

          <div className="memo-meta">
            <span>Sections Analyzed: {memo.sections_analyzed.join(', ')}</span>
            <span>Generated: {new Date(memo.generated_at).toLocaleString()}</span>
          </div>

          <div className="memo-content">
            <pre>{memo.memo}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default MemoGenerator;
