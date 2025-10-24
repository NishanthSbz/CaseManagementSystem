import axios from 'axios';
import { useAuthStore } from '../store/authStore';
import { toast } from 'react-toastify';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  validateStatus: function (status) {
    return status >= 200 && status < 500; // Handle all responses except server errors
  },
  withCredentials: true, // Important for CORS requests with credentials
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response } = error;
    
    if (response?.status === 401 && window.location.pathname !== '/login') {
      // Only handle 401 for authenticated routes, not login attempts
      const authStore = useAuthStore.getState();
      authStore.logout();
      toast.error('Session expired. Please login again.');
      window.location.href = '/login';
    } else if (response?.status === 403) {
      toast.error('Access denied. Insufficient permissions.');
    } else if (response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    
    return Promise.reject(error);
  }
);

export default api;