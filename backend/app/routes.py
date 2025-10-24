from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.auth import auth_required, register_user, login_user, refresh_token, logout_user, get_current_user
from app.services.simplified_case_service import SimplifiedCaseService
from app.authorization import require_case_access, get_accessible_cases_query, authorize_case_access

api = Blueprint('api', __name__)

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status_code = register_user(data)
    return jsonify(result), status_code

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status_code = login_user(data)
    return jsonify(result), status_code

@api.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    result, status_code = refresh_token()
    return jsonify(result), status_code

@api.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    result, status_code = logout_user()
    return jsonify(result), status_code

@api.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    result, status_code = get_current_user()
    return jsonify(result), status_code

@api.route('/cases', methods=['POST'])
@auth_required()
@require_case_access('create')
def create_case(current_user, case_id=None):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status_code = SimplifiedCaseService.create_case(data, current_user)
    return jsonify(result), status_code

@api.route('/cases', methods=['GET'])
@auth_required()
def get_cases(current_user):
    query_params = request.args.to_dict()
    result, status_code = SimplifiedCaseService.get_cases(query_params, current_user)
    return jsonify(result), status_code

@api.route('/cases/<int:case_id>', methods=['GET'])
@auth_required()
@require_case_access('read')
def get_case(current_user, case_id, case):
    """
    Get a single case.
    
    Authorization:
    - Admin: Can view any case
    - User: Can only view cases they own
    """
    result, status_code = SimplifiedCaseService.get_case(case_id, current_user)
    return jsonify(result), status_code

@api.route('/cases/<int:case_id>', methods=['PATCH'])
@auth_required()
@require_case_access('write')
def update_case(current_user, case_id, case):
    """
    Update a case.
    
    Authorization:
    - Admin: Can update any case
    - User: Can only update cases they own, and not if status is 'closed'
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status_code = SimplifiedCaseService.update_case(case_id, data, current_user)
    return jsonify(result), status_code

@api.route('/cases/<int:case_id>', methods=['DELETE'])
@auth_required()
@require_case_access('delete')
def delete_case(current_user, case_id, case):
    result, status_code = SimplifiedCaseService.delete_case(case_id, current_user)
    return jsonify(result), status_code

@api.route('/users', methods=['GET'])
@auth_required()
def get_users(current_user):
    from app.models import User
    from app.rbac import RBACManager, Permission, AuditLogger
    
    if RBACManager.has_permission(current_user, Permission.ASSIGN_CASES):
        users = User.query.filter_by(is_active=True).all()
        AuditLogger.log_action(
            current_user.id, "GET_ALL_USERS", "USER",
            result="SUCCESS", details="Admin accessed full user list"
        )
    else:
        users = [current_user]
        AuditLogger.log_action(
            current_user.id, "GET_SELF_USER", "USER",
            result="SUCCESS", details="User accessed own profile only"
        )
    
    return jsonify({
        'users': [{'id': user.id, 'username': user.username, 'email': user.email} 
                 for user in users]
    }), 200

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Case Management API is running'
    }), 200

@api.route('/test-auth', methods=['GET'])
@auth_required()
def test_auth(current_user):
    return jsonify({
        'message': 'Authentication successful',
        'user': current_user.username,
        'is_admin': current_user.is_admin()
    }), 200

@api.route('/test-no-auth', methods=['GET'])
def test_no_auth():
    return jsonify({
        'message': 'No auth test successful',
        'params': request.args.to_dict()
    }), 200

@api.route('/admin/users', methods=['GET'])
@auth_required(admin_only=True)
def get_all_users(current_user):
    from app.models import User
    
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve users', 'details': str(e)}), 500

@api.route('/admin/audit-logs', methods=['GET'])
@auth_required(admin_only=True)
def get_audit_logs(current_user):
    from app.models import AuditLog
    from app.rbac import RBACManager, Permission, AuditLogger
    
    # Check specific permission for audit logs
    if not RBACManager.has_permission(current_user, Permission.VIEW_AUDIT_LOGS):
        AuditLogger.log_action(
            current_user.id, "VIEW_AUDIT_LOGS", "AUDIT",
            result="FORBIDDEN", details="Missing VIEW_AUDIT_LOGS permission"
        )
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Parse query parameters
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(max(1, int(request.args.get('per_page', 50))), 100)
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    result_filter = request.args.get('result')
    
    # Build query
    query = AuditLog.query
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f'%{action}%'))
    if result_filter:
        query = query.filter(AuditLog.result == result_filter)
    
    # Order by timestamp (newest first)
    query = query.order_by(AuditLog.timestamp.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    AuditLogger.log_action(
        current_user.id, "VIEW_AUDIT_LOGS", "AUDIT",
        result="SUCCESS", details=f"Viewed page {page}"
    )
    
    return jsonify({
        'audit_logs': [log.to_dict() for log in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@api.route('/admin/permissions/<int:user_id>', methods=['GET'])
@auth_required(admin_only=True)
def get_user_permissions(current_user, user_id):
    from app.models import User
    from app.rbac import RBACManager, AuditLogger
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    permissions = RBACManager.get_user_permissions(target_user)
    
    AuditLogger.log_action(
        current_user.id, "VIEW_USER_PERMISSIONS", "USER", user_id,
        result="SUCCESS", details=f"Viewed permissions for {target_user.username}"
    )
    
    return jsonify({
        'user': target_user.to_dict(),
        'permissions': [p.value for p in permissions]
    }), 200

@api.route('/admin/cases', methods=['GET'])
@auth_required(admin_only=True)
def get_all_cases_admin(current_user):
    from app.models import Case
    
    try:
        query_params = request.args.to_dict()
        
        query = Case.query
        
        if query_params.get('status'):
            query = query.filter(Case.status == query_params['status'])
        
        if query_params.get('is_active') == 'false':
            query = query.filter(Case.is_active == False)
        else:
            query = query.filter(Case.is_active == True)
        
        cases = query.order_by(Case.created_at.desc()).all()
        
        return jsonify({
            'cases': [case.to_dict() for case in cases]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve cases', 'details': str(e)}), 500