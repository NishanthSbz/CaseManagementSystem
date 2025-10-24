import api from './api';

export const authAPI = {
  // Register new user
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response.data.error) {
        throw new Error(response.data.error);
      }
      return response.data;
    } catch (error) {
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  // Refresh access token
  refresh: async () => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },

  // Logout user
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  // Get current user
  me: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

export const casesAPI = {
  // Get all cases with pagination and filters
  getCases: async (params = {}) => {
    const response = await api.get('/cases', { params });
    return response.data;
  },

  // Get single case
  getCase: async (id) => {
    const response = await api.get(`/cases/${id}`);
    return response.data;
  },

  // Create new case
  createCase: async (caseData) => {
    const response = await api.post('/cases', caseData);
    return response.data;
  },

  // Update case
  updateCase: async (id, updates) => {
    const response = await api.patch(`/cases/${id}`, updates);
    return response.data;
  },

  // Delete case
  deleteCase: async (id) => {
    const response = await api.delete(`/cases/${id}`);
    return response.data;
  }
};

export const usersAPI = {
  // Get all users for case assignment
  getUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  }
};

export const adminAPI = {
  // Get all users (admin only)
  getUsers: async () => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  // Get all cases including inactive (admin only)
  getAllCases: async (params = {}) => {
    const response = await api.get('/admin/cases', { params });
    return response.data;
  }
};