import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useCaseStore } from '../store/caseStore';
import { useAuthStore } from '../store/authStore';
import { usersAPI } from '../api';
import { Modal } from './Modal';
import { format } from 'date-fns';
import { RBACHelper } from '../utils/rbac';

export const CaseForm = ({ isOpen, onClose, case: editCase = null }) => {
  const { createCase, updateCase, isCreating, isUpdating } = useCaseStore();
  const { user } = useAuthStore();
  const [users, setUsers] = useState([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm({
    defaultValues: editCase ? {
      title: editCase.title || '',
      description: editCase.description || '',
      priority: editCase.priority || 'medium',
      status: editCase.status || 'open',
      due_date: editCase.due_date ? format(new Date(editCase.due_date), "yyyy-MM-dd'T'HH:mm") : '',
      assigned_to: editCase.assigned_to || '',
    } : {
      title: '',
      description: '',
      priority: 'medium',
      status: 'open',
      due_date: '',
      assigned_to: '',
    }
  });

  // Load users for assignment dropdown
  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await usersAPI.getUsers();
        // Filter users based on assignment permissions
        const availableUsers = RBACHelper.canAssignCases(user) 
          ? data.users 
          : data.users.filter(u => u.id === user.id);
        setUsers(availableUsers);
      } catch (error) {
        console.error('Failed to load users:', error);
        // If user can't assign cases, only show themselves
        if (!RBACHelper.canAssignCases(user)) {
          setUsers([user]);
        }
      }
    };
    
    if (isOpen) {
      loadUsers();
    }
  }, [isOpen]);

  const currentStatus = watch('status');
  const isEditing = Boolean(editCase);
  const isLoading = isCreating || isUpdating;

  // Get valid status transitions
  const getValidStatusOptions = () => {
    if (!isEditing) {
      return [{ value: 'open', label: 'Open' }];
    }

    const statusTransitions = {
      open: ['open', 'in_progress'],
      in_progress: ['in_progress', 'closed'],
      closed: ['closed'],
    };

    const validStatuses = statusTransitions[editCase?.status] || ['open'];
    
    return [
      { value: 'open', label: 'Open' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'closed', label: 'Closed' },
    ].filter(option => validStatuses.includes(option.value));
  };

  const onSubmit = async (data) => {
    // Format due_date
    const formattedData = {
      ...data,
      due_date: data.due_date ? new Date(data.due_date).toISOString() : null,
      assigned_to: data.assigned_to || null,
    };

    let result;
    if (isEditing) {
      result = await updateCase(editCase.id, formattedData);
    } else {
      result = await createCase(formattedData);
    }

    if (result.success) {
      reset();
      onClose();
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={isEditing ? 'Edit Case' : 'Create New Case'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            id="title"
            {...register('title', { 
              required: 'Title is required',
              minLength: { value: 1, message: 'Title cannot be empty' },
              maxLength: { value: 200, message: 'Title must be less than 200 characters' }
            })}
            className="input"
            placeholder="Enter case title"
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            rows={4}
            {...register('description')}
            className="input resize-none"
            placeholder="Enter case description"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Priority */}
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              {...register('priority')}
              className="input"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              {...register('status')}
              className="input"
              disabled={!isEditing}
            >
              {getValidStatusOptions().map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {isEditing && (
              <p className="mt-1 text-xs text-gray-500">
                Status transitions: Open → In Progress → Closed
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Due Date */}
          <div>
            <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <input
              type="datetime-local"
              id="due_date"
              {...register('due_date')}
              className="input"
              min={new Date().toISOString().slice(0, 16)}
            />
          </div>

          {/* Assigned To */}
          {RBACHelper.canAssignCases(user) && (
            <div>
              <label htmlFor="assigned_to" className="block text-sm font-medium text-gray-700 mb-1">
                Assigned To
              </label>
              <select
                id="assigned_to"
                {...register('assigned_to')}
                className="input"
              >
                <option value="">Unassigned</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>
                    {u.username} ({u.email})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={handleClose}
            className="btn btn-secondary"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {isEditing ? 'Updating...' : 'Creating...'}
              </span>
            ) : (
              isEditing ? 'Update Case' : 'Create Case'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};