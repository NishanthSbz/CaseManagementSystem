from enum import Enum
from functools import wraps
from flask import jsonify, request, g
from datetime import datetime
from app.models import User, Case
from app import db
import logging

audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler('audit.log')
audit_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - User:%(user_id)s - Action:%(action)s - Resource:%(resource)s - Result:%(result)s - Details:%(details)s'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

class Permission(Enum):
    VIEW_ALL_CASES = "view_all_cases"
    VIEW_OWN_CASES = "view_own_cases"
    VIEW_ASSIGNED_CASES = "view_assigned_cases"
    CREATE_CASE = "create_case"
    EDIT_OWN_CASES = "edit_own_cases"
    EDIT_ALL_CASES = "edit_all_cases"
    DELETE_OWN_CASES = "delete_own_cases"
    DELETE_ALL_CASES = "delete_all_cases"
    ASSIGN_CASES = "assign_cases"
    UPDATE_STATUS_OWN = "update_status_own"
    UPDATE_STATUS_ASSIGNED = "update_status_assigned"
    UPDATE_STATUS_ALL = "update_status_all"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_ALL_CASES,
        Permission.CREATE_CASE,
        Permission.EDIT_ALL_CASES,
        Permission.DELETE_ALL_CASES,
        Permission.ASSIGN_CASES,
        Permission.UPDATE_STATUS_ALL,
        Permission.MANAGE_USERS,
        Permission.VIEW_AUDIT_LOGS,
    ],
    Role.USER: [
        Permission.VIEW_OWN_CASES,
        Permission.VIEW_ASSIGNED_CASES,
        Permission.CREATE_CASE,
        Permission.EDIT_OWN_CASES,
        Permission.DELETE_OWN_CASES,
        Permission.UPDATE_STATUS_OWN,
        Permission.UPDATE_STATUS_ASSIGNED,
    ],
    Role.MANAGER: [  # Future role
        Permission.VIEW_ALL_CASES,
        Permission.CREATE_CASE,
        Permission.EDIT_ALL_CASES,
        Permission.ASSIGN_CASES,
        Permission.UPDATE_STATUS_ALL,
    ],
    Role.VIEWER: [  # Future role
        Permission.VIEW_OWN_CASES,
        Permission.VIEW_ASSIGNED_CASES,
    ],
}

class RBACManager:
    @staticmethod
    def has_permission(user, permission, resource=None):
        if not user or not user.is_active:
            return False
        
        try:
            user_role = Role(user.role)
        except ValueError:
            return False
        
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        if permission not in user_permissions:
            return False
        
        # Resource-specific checks
        if resource and isinstance(resource, Case):
            return RBACManager._check_case_permission(user, permission, resource)
        
        return True
    
    @staticmethod
    def _check_case_permission(user, permission, case):
        """Check case-specific permissions"""
        is_owner = case.created_by == user.id
        is_assignee = case.assigned_to == user.id
        
        # Permission-specific logic
        if permission in [Permission.EDIT_OWN_CASES, Permission.DELETE_OWN_CASES]:
            return is_owner
        elif permission == Permission.UPDATE_STATUS_OWN:
            return is_owner
        elif permission == Permission.UPDATE_STATUS_ASSIGNED:
            return is_assignee
        elif permission in [Permission.VIEW_OWN_CASES]:
            return is_owner
        elif permission == Permission.VIEW_ASSIGNED_CASES:
            return is_assignee
        
        return True  # Admin permissions pass through
    
    @staticmethod
    def get_user_permissions(user):
        if not user:
            return []
        
        try:
            user_role = Role(user.role)
            return ROLE_PERMISSIONS.get(user_role, [])
        except ValueError:
            return []
    
    @staticmethod
    def can_view_case(user, case):
        if RBACManager.has_permission(user, Permission.VIEW_ALL_CASES):
            return True
        
        if (RBACManager.has_permission(user, Permission.VIEW_OWN_CASES) and 
            case.created_by == user.id):
            return True
        
        if (RBACManager.has_permission(user, Permission.VIEW_ASSIGNED_CASES) and 
            case.assigned_to == user.id):
            return True
        
        return False
    
    @staticmethod
    def can_edit_case(user, case):
        if RBACManager.has_permission(user, Permission.EDIT_ALL_CASES):
            return True
        
        if (RBACManager.has_permission(user, Permission.EDIT_OWN_CASES) and 
            case.created_by == user.id):
            return True
        
        return False
    
    @staticmethod
    def can_delete_case(user, case):
        if RBACManager.has_permission(user, Permission.DELETE_ALL_CASES):
            return True
        
        if (RBACManager.has_permission(user, Permission.DELETE_OWN_CASES) and 
            case.created_by == user.id):
            return True
        
        return False
    
    @staticmethod
    def can_update_case_status(user, case):
        if RBACManager.has_permission(user, Permission.UPDATE_STATUS_ALL):
            return True
        
        if (RBACManager.has_permission(user, Permission.UPDATE_STATUS_OWN) and 
            case.created_by == user.id):
            return True
        
        if (RBACManager.has_permission(user, Permission.UPDATE_STATUS_ASSIGNED) and 
            case.assigned_to == user.id):
            return True
        
        return False

class AuditLogger:
    @staticmethod
    def log_action(user_id, action, resource_type, resource_id=None, result="SUCCESS", details=""):
        audit_logger.info(
            f"",
            extra={
                'user_id': user_id,
                'action': action,
                'resource': f"{resource_type}:{resource_id}" if resource_id else resource_type,
                'result': result,
                'details': details
            }
        )
        
        # Store in database for queryable audit trail
        try:
            from app.models import AuditLog
            from app import db
            
            audit_record = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                result=result,
                details=details,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(audit_record)
            db.session.commit()
            
        except Exception as e:
            print(f"Audit logging failed: {e}")
            # Don't fail the main operation if audit logging fails
            try:
                db.session.rollback()
            except:
                pass

def require_permission(permission, resource_loader=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                AuditLogger.log_action(
                    None, f.__name__, "ENDPOINT", 
                    result="UNAUTHORIZED", details="No authenticated user"
                )
                return jsonify({'error': 'Authentication required'}), 401
            
            user = g.current_user
            resource = None
            
            if resource_loader:
                try:
                    resource = resource_loader(*args, **kwargs)
                except Exception as e:
                    AuditLogger.log_action(
                        user.id, f.__name__, "ENDPOINT",
                        result="ERROR", details=f"Resource loading failed: {e}"
                    )
                    return jsonify({'error': 'Resource not found'}), 404
            
            if not RBACManager.has_permission(user, permission, resource):
                AuditLogger.log_action(
                    user.id, f.__name__, "ENDPOINT",
                    result="FORBIDDEN", 
                    details=f"Missing permission: {permission.value}"
                )
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            AuditLogger.log_action(
                user.id, f.__name__, "ENDPOINT",
                result="SUCCESS", details=f"Permission: {permission.value}"
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def case_loader(case_id):
    return Case.query.filter_by(id=case_id, is_active=True).first()