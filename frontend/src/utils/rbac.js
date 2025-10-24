// Enhanced RBAC utilities for frontend
export const PERMISSIONS = {
  VIEW_ALL_CASES: 'view_all_cases',
  VIEW_OWN_CASES: 'view_own_cases',
  VIEW_ASSIGNED_CASES: 'view_assigned_cases',
  CREATE_CASE: 'create_case',
  EDIT_OWN_CASES: 'edit_own_cases',
  EDIT_ALL_CASES: 'edit_all_cases',
  DELETE_OWN_CASES: 'delete_own_cases',
  DELETE_ALL_CASES: 'delete_all_cases',
  ASSIGN_CASES: 'assign_cases',
  UPDATE_STATUS_OWN: 'update_status_own',
  UPDATE_STATUS_ASSIGNED: 'update_status_assigned',
  UPDATE_STATUS_ALL: 'update_status_all',
  MANAGE_USERS: 'manage_users',
  VIEW_AUDIT_LOGS: 'view_audit_logs',
};

export const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  MANAGER: 'manager',
  VIEWER: 'viewer',
};

// Role-Permission Matrix (matches backend)
const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.VIEW_ALL_CASES,
    PERMISSIONS.CREATE_CASE,
    PERMISSIONS.EDIT_ALL_CASES,
    PERMISSIONS.DELETE_ALL_CASES,
    PERMISSIONS.ASSIGN_CASES,
    PERMISSIONS.UPDATE_STATUS_ALL,
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.VIEW_AUDIT_LOGS,
  ],
  [ROLES.USER]: [
    PERMISSIONS.VIEW_OWN_CASES,
    PERMISSIONS.VIEW_ASSIGNED_CASES,
    PERMISSIONS.CREATE_CASE,
    PERMISSIONS.EDIT_OWN_CASES,
    PERMISSIONS.DELETE_OWN_CASES,
    PERMISSIONS.UPDATE_STATUS_OWN,
    PERMISSIONS.UPDATE_STATUS_ASSIGNED,
  ],
  [ROLES.MANAGER]: [
    PERMISSIONS.VIEW_ALL_CASES,
    PERMISSIONS.CREATE_CASE,
    PERMISSIONS.EDIT_ALL_CASES,
    PERMISSIONS.ASSIGN_CASES,
    PERMISSIONS.UPDATE_STATUS_ALL,
  ],
  [ROLES.VIEWER]: [
    PERMISSIONS.VIEW_OWN_CASES,
    PERMISSIONS.VIEW_ASSIGNED_CASES,
  ],
};

export class RBACHelper {
  /**
   * Check if user has a specific permission
   * @param {Object} user - User object with role
   * @param {string} permission - Permission to check
   * @param {Object} resource - Optional resource for context-specific checks
   * @returns {boolean}
   */
  static hasPermission(user, permission, resource = null) {
    if (!user || !user.role) return false;
    
    const userPermissions = ROLE_PERMISSIONS[user.role] || [];
    
    // Check basic permission
    if (!userPermissions.includes(permission)) {
      return false;
    }
    
    // Resource-specific checks for cases
    if (resource && resource.id) {
      return this._checkCasePermission(user, permission, resource);
    }
    
    return true;
  }
  
  /**
   * Check case-specific permissions
   * @private
   */
  static _checkCasePermission(user, permission, caseObj) {
    const isOwner = caseObj.created_by === user.id;
    const isAssignee = caseObj.assigned_to === user.id;
    
    switch (permission) {
      case PERMISSIONS.EDIT_OWN_CASES:
      case PERMISSIONS.DELETE_OWN_CASES:
        return isOwner;
      
      case PERMISSIONS.UPDATE_STATUS_OWN:
        return isOwner;
      
      case PERMISSIONS.UPDATE_STATUS_ASSIGNED:
        return isAssignee;
      
      case PERMISSIONS.VIEW_OWN_CASES:
        return isOwner;
      
      case PERMISSIONS.VIEW_ASSIGNED_CASES:
        return isAssignee;
      
      default:
        return true; // Admin permissions pass through
    }
  }
  
  /**
   * Check if user can view a specific case
   */
  static canViewCase(user, caseObj) {
    if (this.hasPermission(user, PERMISSIONS.VIEW_ALL_CASES)) {
      return true;
    }
    
    if (this.hasPermission(user, PERMISSIONS.VIEW_OWN_CASES) && 
        caseObj.created_by === user.id) {
      return true;
    }
    
    if (this.hasPermission(user, PERMISSIONS.VIEW_ASSIGNED_CASES) && 
        caseObj.assigned_to === user.id) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Check if user can edit a specific case
   */
  static canEditCase(user, caseObj) {
    if (this.hasPermission(user, PERMISSIONS.EDIT_ALL_CASES)) {
      return true;
    }
    
    if (this.hasPermission(user, PERMISSIONS.EDIT_OWN_CASES) && 
        caseObj.created_by === user.id) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Check if user can delete a specific case
   */
  static canDeleteCase(user, caseObj) {
    if (this.hasPermission(user, PERMISSIONS.DELETE_ALL_CASES)) {
      return true;
    }
    
    if (this.hasPermission(user, PERMISSIONS.DELETE_OWN_CASES) && 
        caseObj.created_by === user.id) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Check if user can update case status
   */
  static canUpdateCaseStatus(user, caseObj) {
    if (this.hasPermission(user, PERMISSIONS.UPDATE_STATUS_ALL)) {
      return true;
    }
    
    if (this.hasPermission(user, PERMISSIONS.UPDATE_STATUS_OWN) && 
        caseObj.created_by === user.id) {
      return true;
    }
    
    if (this.hasPermission(user, PERMISSIONS.UPDATE_STATUS_ASSIGNED) && 
        caseObj.assigned_to === user.id) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Get all fields a user can edit for a case
   */
  static getEditableFields(user, caseObj) {
    const fields = new Set();
    
    if (this.canEditCase(user, caseObj)) {
      fields.add('title');
      fields.add('description');
      fields.add('priority');
      fields.add('due_date');
      fields.add('status');
      
      if (this.hasPermission(user, PERMISSIONS.ASSIGN_CASES)) {
        fields.add('assigned_to');
      }
    } else if (this.canUpdateCaseStatus(user, caseObj)) {
      fields.add('status');
    }
    
    return Array.from(fields);
  }
  
  /**
   * Get user's role display name
   */
  static getRoleDisplayName(role) {
    const roleNames = {
      [ROLES.ADMIN]: 'Administrator',
      [ROLES.USER]: 'User',
      [ROLES.MANAGER]: 'Manager',
      [ROLES.VIEWER]: 'Viewer',
    };
    
    return roleNames[role] || 'Unknown';
  }
  
  /**
   * Check if user is admin (convenience method)
   */
  static isAdmin(user) {
    return user && user.role === ROLES.ADMIN;
  }

  /**
   * Check if user can assign cases to other users
   */
  static canAssignCases(user) {
    return this.hasPermission(user, PERMISSIONS.ASSIGN_CASES);
  }
}

export default RBACHelper;