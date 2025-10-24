from functools import wraps
from flask import jsonify
from app.models import Case, User

def authorize_case_access(case, current_user, action='read'):
    if current_user.role == 'admin':
        return True, None
    
    if action == 'create':
        return True, None
    
    if not case:
        return False, {'error': 'Unauthorized access'}
    
    is_owner = case.created_by == current_user.id
    is_assigned = case.assigned_to == current_user.id
    
    if action == 'read':
        if not (is_owner or is_assigned):
            return False, {'error': 'Unauthorized access'}
    else:
        if not is_owner:
            return False, {'error': 'Unauthorized access'}
        
        if case.status == 'closed':
            return False, {'error': 'Unauthorized access'}
    
    return True, None


def require_case_access(action='read'):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, case_id=None, *args, **kwargs):
            # For operations that need a case, fetch it
            case = None
            if case_id and action != 'create':
                case = Case.query.filter_by(id=case_id, is_active=True).first()
                if not case:
                    return jsonify({'error': 'Case not found'}), 404
            
            # Check authorization
            authorized, error_response = authorize_case_access(case, current_user, action)
            if not authorized:
                return jsonify(error_response), 403
            
            # If case was fetched, pass it to the route function
            if case:
                return f(current_user, case_id, case, *args, **kwargs)
            else:
                return f(current_user, case_id, *args, **kwargs)
                
        return decorated_function
    return decorator


def get_accessible_cases_query(current_user):
    """
    Get a query for cases that the current user can access.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        SQLAlchemy query filtered for user's accessible cases
        
    Access Rules:
        - Admin: Returns all active cases
        - User: Returns cases where owner_id == current_user.id OR assigned_to == current_user.id
    """
    from sqlalchemy import or_
    
    base_query = Case.query.filter(Case.is_active == True)
    
    if current_user.role == 'admin':
        # Admin can see all cases
        return base_query
    else:
        # Users can see cases they own OR are assigned to
        return base_query.filter(
            or_(
                Case.created_by == current_user.id,
                Case.assigned_to == current_user.id
            )
        )


def can_modify_case(case, current_user):
    """
    Check if user can modify a specific case.
    
    Args:
        case: Case object
        current_user: Current authenticated user
        
    Returns:
        bool: True if user can modify the case
        
    Business Rules:
        - Admin: Can modify any case
        - User: Can modify only their own cases that are not closed
    """
    if current_user.role == 'admin':
        return True
    
    # Users can only modify their own non-closed cases
    return (case.created_by == current_user.id and case.status != 'closed')


def can_delete_case(case, current_user):
    """
    Check if user can delete a specific case.
    
    Args:
        case: Case object
        current_user: Current authenticated user
        
    Returns:
        bool: True if user can delete the case
        
    Business Rules:
        - Admin: Can delete any case
        - User: Can delete only their own cases that are not closed
    """
    if current_user.role == 'admin':
        return True
    
    # Users can only delete their own non-closed cases
    return (case.created_by == current_user.id and case.status != 'closed')