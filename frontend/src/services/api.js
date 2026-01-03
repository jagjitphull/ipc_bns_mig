import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Section endpoints
  getSections: (params = {}) => api.get('/sections', { params }),
  getSection: (ipcSection) => api.get(`/section/${ipcSection}`),
  analyzeSection: (ipcSection) => api.post('/analyze', { ipc_section: ipcSection }),

  // Memo generation
  generateMemo: (ipcSections, context = '') =>
    api.post('/memo', { ipc_sections: ipcSections, query_context: context }),

  // Case search
  searchCases: (query, nResults = 5) =>
    api.post('/cases/search', { query, n_results: nResults }),
  getCases: (params = {}) => api.get('/cases', { params }),
  getCase: (caseId) => api.get(`/cases/${caseId}`),

  // Statistics
  getStats: () => api.get('/stats'),
  getCategories: () => api.get('/categories'),
};

export default api;
