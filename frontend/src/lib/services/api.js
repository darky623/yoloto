const API_BASE = import.meta.env.VITE_API_BASE || '/api';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || error.message || 'Request failed');
  }
  
  return response.json();
}

export const api = {
  // Auth
  async register(data) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  async login(data) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  async getMe() {
    return request('/auth/me');
  },
  
  // Tables
  async getTables() {
    return request('/tables');
  },
  
  async getTable(tableId) {
    return request(`/tables/${tableId}`);
  },
  
  async joinTable(tableId) {
    return request(`/tables/${tableId}/join`, {
      method: 'POST'
    });
  },
  
  async leaveTable(tableId) {
    return request(`/tables/${tableId}/leave`, {
      method: 'POST'
    });
  },
  
  // User
  async getBalance() {
    return request('/user/balance');
  }
};

