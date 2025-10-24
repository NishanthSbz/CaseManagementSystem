import { useState, useEffect } from 'react';
import { Search, Plus, Filter, Edit, Trash2, Eye, Shield } from 'lucide-react';
import { useCaseStore } from '../store/caseStore';
import { useAuthStore } from '../store/authStore';
import { StatusBadge, PriorityBadge, TableSkeleton } from './UI';
import { CaseForm } from './CaseForm';
import { Modal } from './Modal';
import { format } from 'date-fns';
import { RBACHelper, PERMISSIONS } from '../utils/rbac';

export const CaseList = () => {
  const {
    cases,
    pagination,
    filters,
    isLoading,
    fetchCases,
    deleteCase,
    setFilters,
    clearCurrentCase,
  } = useCaseStore();
  
  const { isAdmin, isAuthenticated, token, user } = useAuthStore();
  
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Enhanced permission helpers using RBAC
  const canCreateCase = () => {
    return RBACHelper.hasPermission(user, PERMISSIONS.CREATE_CASE);
  };

  const canEditCase = (case_) => {
    return RBACHelper.canEditCase(user, case_);
  };

  const canDeleteCase = (case_) => {
    return RBACHelper.canDeleteCase(user, case_);
  };

  const canUpdateStatus = (case_) => {
    return RBACHelper.canUpdateCaseStatus(user, case_);
  };

  const getCaseIndicator = (case_) => {
    if (!user) return null;
    
    if (case_.created_by === user.id) {
      return { type: 'owner', label: 'Owner', color: 'bg-blue-100 text-blue-800' };
    } else if (case_.assigned_to === user.id) {
      return { type: 'assigned', label: 'Assigned', color: 'bg-green-100 text-green-800' };
    }
    
    return null;
  };

  // Load cases on component mount and when filters change
  useEffect(() => {
    if (isAuthenticated && token) {
      loadCases();
    }
  }, [filters, currentPage, isAuthenticated, token]);

  const loadCases = async () => {
    if (!isAuthenticated || !token) {
      console.log('User not authenticated, skipping case fetch');
      return;
    }
    
    const params = {
      page: currentPage,
      per_page: 10,
      ...Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== '')
      ),
    };
    console.log('Loading cases with authenticated user');
    await fetchCases(params);
  };

  const handleSearch = (e) => {
    setFilters({ search: e.target.value });
    setCurrentPage(1);
  };

  const handleFilterChange = (key, value) => {
    setFilters({ [key]: value });
    setCurrentPage(1);
  };

  const handleCreateCase = () => {
    setEditingCase(null);
    clearCurrentCase();
    setIsFormOpen(true);
  };

  const handleEditCase = (case_) => {
    setEditingCase(case_);
    setIsFormOpen(true);
  };

  const handleDeleteCase = async (case_) => {
    const result = await deleteCase(case_.id);
    if (result.success) {
      setDeleteConfirm(null);
      // Reload current page if it becomes empty
      if (cases.length === 1 && currentPage > 1) {
        setCurrentPage(currentPage - 1);
      } else {
        loadCases();
      }
    }
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return 'Invalid Date';
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return 'Invalid Date';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
          <p className="text-gray-600">
            {RBACHelper.isAdmin(user) 
              ? 'Manage and track all cases' 
              : 'Manage your cases and assignments'
            }
          </p>
        </div>
        {canCreateCase() && (
          <button
            onClick={handleCreateCase}
            className="btn btn-primary btn-md flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Case
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search cases..."
                value={filters.search}
                onChange={handleSearch}
                className="input pl-10"
              />
            </div>

            {/* Status Filter */}
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="closed">Closed</option>
            </select>

            {/* Priority Filter */}
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="input"
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>

            {/* Clear Filters */}
            <button
              onClick={() => {
                setFilters({ status: '', priority: '', search: '' });
                setCurrentPage(1);
              }}
              className="btn btn-secondary flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Cases Table */}
      <div className="card">
        <div className="card-content p-0">
          {isLoading ? (
            <div className="p-6">
              <TableSkeleton rows={5} cols={6} />
            </div>
          ) : cases.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Eye className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No cases found</h3>
              <p className="text-gray-600 mb-4">
                {Object.values(filters).some(v => v) 
                  ? 'No cases match your current filters.'
                  : 'Get started by creating your first case.'
                }
              </p>
              <button
                onClick={handleCreateCase}
                className="btn btn-primary"
              >
                Create First Case
              </button>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Priority
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Due Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Assigned To
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created By
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {cases.map((case_) => (
                      <tr key={case_.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                                {case_.title}
                              </div>
                              {(() => {
                                const indicator = getCaseIndicator(case_);
                                return indicator ? (
                                  <span className={`px-2 py-1 text-xs rounded-full ${indicator.color}`}>
                                    {indicator.label}
                                  </span>
                                ) : null;
                              })()}
                            </div>
                            {case_.description && (
                              <div className="text-sm text-gray-500 truncate max-w-xs">
                                {case_.description}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <StatusBadge status={case_.status} />
                        </td>
                        <td className="px-6 py-4">
                          <PriorityBadge priority={case_.priority} />
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {formatDate(case_.due_date)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {case_.assignee || 'Unassigned'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {case_.creator || 'Unknown'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {formatDate(case_.created_at)}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {canEditCase(case_) && (
                              <button
                                onClick={() => handleEditCase(case_)}
                                className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                                title="Edit case"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                            )}
                            {canDeleteCase(case_) && (
                              <button
                                onClick={() => setDeleteConfirm(case_)}
                                className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                                title="Delete case"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                            {/* Show view-only indicator for assigned cases */}
                            {!canEditCase(case_) && canUpdateStatus(case_) && (
                              <span className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                                Assigned
                              </span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {pagination && pagination.pages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-700">
                      Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
                      {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
                      {pagination.total} results
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={!pagination.has_prev}
                        className="btn btn-secondary btn-sm disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <span className="text-sm text-gray-700">
                        Page {pagination.page} of {pagination.pages}
                      </span>
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={!pagination.has_next}
                        className="btn btn-secondary btn-sm disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Case Form Modal */}
      <CaseForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingCase(null);
        }}
        case={editingCase}
      />

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <Modal
          isOpen={true}
          onClose={() => setDeleteConfirm(null)}
          title="Delete Case"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete "{deleteConfirm.title}"? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteCase(deleteConfirm)}
                className="btn btn-danger"
              >
                Delete
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};