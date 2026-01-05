import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          // Try to refresh the token
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            {},
            {
              headers: { Authorization: `Bearer ${refreshToken}` }
            }
          );

          if (response.data.access_token) {
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);

            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

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
  generateMemoPDF: (ipcSections, context = '') =>
    api.post('/memo/pdf', { ipc_sections: ipcSections, query_context: context }, { responseType: 'blob' }),

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
