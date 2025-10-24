import { create } from 'zustand';
import { casesAPI } from '../api';
import { toast } from 'react-toastify';

export const useCaseStore = create((set, get) => ({
  // State
  cases: [],
  currentCase: null,
  pagination: null,
  filters: {
    status: '',
    priority: '',
    search: '',
  },
  isLoading: false,
  isCreating: false,
  isUpdating: false,

  // Actions
  fetchCases: async (params = {}) => {
    set({ isLoading: true });
    try {
      console.log('Fetching cases with params:', params);
      const data = await casesAPI.getCases(params);
      console.log('Cases data received:', data);
      set({
        cases: data.cases,
        pagination: data.pagination,
        isLoading: false,
      });
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching cases:', error);
      console.error('Error response:', error.response);
      set({ isLoading: false });
      const message = error.response?.data?.error || error.message || 'Failed to fetch cases';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  fetchCase: async (id) => {
    set({ isLoading: true });
    try {
      const data = await casesAPI.getCase(id);
      set({
        currentCase: data.case,
        isLoading: false,
      });
      return { success: true, data };
    } catch (error) {
      set({ isLoading: false });
      const message = error.response?.data?.error || 'Failed to fetch case';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  createCase: async (caseData) => {
    set({ isCreating: true });
    try {
      const data = await casesAPI.createCase(caseData);
      
      // Add new case to the list
      set((state) => ({
        cases: [data.case, ...state.cases],
        isCreating: false,
      }));
      
      toast.success('Case created successfully!');
      return { success: true, data };
    } catch (error) {
      set({ isCreating: false });
      const message = error.response?.data?.error || 'Failed to create case';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  updateCase: async (id, updates) => {
    set({ isUpdating: true });
    try {
      const data = await casesAPI.updateCase(id, updates);
      
      // Update case in the list
      set((state) => ({
        cases: state.cases.map((case_) =>
          case_.id === id ? data.case : case_
        ),
        currentCase: state.currentCase?.id === id ? data.case : state.currentCase,
        isUpdating: false,
      }));
      
      toast.success('Case updated successfully!');
      return { success: true, data };
    } catch (error) {
      set({ isUpdating: false });
      const message = error.response?.data?.error || 'Failed to update case';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  deleteCase: async (id) => {
    try {
      await casesAPI.deleteCase(id);
      
      // Remove case from the list
      set((state) => ({
        cases: state.cases.filter((case_) => case_.id !== id),
        currentCase: state.currentCase?.id === id ? null : state.currentCase,
      }));
      
      toast.success('Case deleted successfully!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to delete case';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }));
  },

  clearFilters: () => {
    set({
      filters: {
        status: '',
        priority: '',
        search: '',
      },
    });
  },

  clearCurrentCase: () => {
    set({ currentCase: null });
  },
}));