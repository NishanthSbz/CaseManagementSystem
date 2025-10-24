from flask import request
from sqlalchemy import and_, or_
from app.models import Case, User
from app.schemas import case_create_schema, case_update_schema, case_query_schema
from app.rbac import RBACManager, Permission, AuditLogger
from app import db

class CaseService:
    @staticmethod
    def create_case(data, current_user):
        if not RBACManager.has_permission(current_user, Permission.CREATE_CASE):
            AuditLogger.log_action(
                current_user.id, "CREATE_CASE", "CASE",
                result="FORBIDDEN", details="Missing CREATE_CASE permission"
            )
            return {'error': 'Insufficient permissions to create cases'}, 403
        
        try:
            if 'assigned_to' in data and data['assigned_to']:
                if data['assigned_to'] != str(current_user.id):
                    if not RBACManager.has_permission(current_user, Permission.ASSIGN_CASES):
                        data['assigned_to'] = str(current_user.id)
                        AuditLogger.log_action(
                            current_user.id, "ASSIGN_CASE_SELF", "CASE",
                            result="CORRECTED", details="Non-admin user can only assign to self"
                        )
                
                try:
                    data['assigned_to'] = int(data['assigned_to'])
                except (ValueError, TypeError):
                    data['assigned_to'] = None
            
            validated_data = case_create_schema.load(data)
        except Exception as e:
            AuditLogger.log_action(
                current_user.id, "CREATE_CASE", "CASE",
                result="VALIDATION_ERROR", details=str(e)
            )
            return {'error': 'Validation failed', 'details': str(e)}, 400
        
        if validated_data.get('assigned_to'):
            assigned_user = User.query.get(validated_data['assigned_to'])
            if not assigned_user or not assigned_user.is_active:
                return {'error': 'Assigned user not found or inactive'}, 400
        
        case = Case(
            title=validated_data['title'],
            description=validated_data['description'],
            priority=validated_data['priority'],
            status=validated_data.get('status', 'open'),
            due_date=validated_data.get('due_date'),
            created_by=current_user.id,
            assigned_to=validated_data.get('assigned_to')
        )
        
        try:
            db.session.add(case)
            db.session.commit()
            
            AuditLogger.log_action(
                current_user.id, "CREATE_CASE", "CASE", case.id,
                result="SUCCESS", 
                details=f"Created case '{case.title}', assigned_to: {case.assigned_to}"
            )
            
            return {'case': case.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            AuditLogger.log_action(
                current_user.id, "CREATE_CASE", "CASE",
                result="ERROR", details=str(e)
            )
            return {'error': 'Failed to create case', 'details': str(e)}, 500
    
    @staticmethod
    def get_cases(query_params, current_user):
        try:
            page = max(1, int(query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
            
        try:
            per_page = min(max(1, int(query_params.get('per_page', 10))), 100)
        except (ValueError, TypeError):
            per_page = 10
            
        validated_params = {
            'page': page,
            'per_page': per_page,
            'status': query_params.get('status') if query_params.get('status') in ['open', 'in_progress', 'closed'] else None,
            'priority': query_params.get('priority') if query_params.get('priority') in ['low', 'medium', 'high'] else None,
            'search': query_params.get('search', '').strip() if query_params.get('search') else ''
        }
        
        # Build base query with RBAC-based access control
        query = Case.query.filter(Case.is_active == True)
        
        # Apply role-based filtering
        if RBACManager.has_permission(current_user, Permission.VIEW_ALL_CASES):
            # Admin can see all cases
            pass
        else:
            # Users can only see cases they created or are assigned to
            accessible_conditions = []
            
            if RBACManager.has_permission(current_user, Permission.VIEW_OWN_CASES):
                accessible_conditions.append(Case.created_by == current_user.id)
            
            if RBACManager.has_permission(current_user, Permission.VIEW_ASSIGNED_CASES):
                accessible_conditions.append(Case.assigned_to == current_user.id)
            
            if accessible_conditions:
                query = query.filter(or_(*accessible_conditions))
            else:
                # User has no view permissions - return empty result
                AuditLogger.log_action(
                    current_user.id, "GET_CASES", "CASE",
                    result="FORBIDDEN", details="No view permissions"
                )
                return {
                    'cases': [],
                    'pagination': {
                        'page': 1, 'per_page': 10, 'total': 0, 'pages': 0,
                        'has_next': False, 'has_prev': False
                    }
                }, 200
        
        # Apply filters
        if validated_params.get('status'):
            query = query.filter(Case.status == validated_params['status'])
        
        if validated_params.get('priority'):
            query = query.filter(Case.priority == validated_params['priority'])
        
        if validated_params.get('assigned_to'):
            query = query.filter(Case.assigned_to == validated_params['assigned_to'])
        
        if validated_params.get('created_by'):
            query = query.filter(Case.created_by == validated_params['created_by'])
        
        if validated_params.get('search'):
            search_term = f"%{validated_params['search']}%"
            query = query.filter(
                or_(
                    Case.title.ilike(search_term),
                    Case.description.ilike(search_term)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Case.created_at.desc())
        
        # Paginate results
        page = validated_params['page']
        per_page = validated_params['per_page']
        
        try:
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'cases': [case.to_dict() for case in pagination.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }, 200
            
        except Exception as e:
            return {'error': 'Failed to retrieve cases', 'details': str(e)}, 500
    
    @staticmethod
    def get_case(case_id, current_user):
        case = Case.query.filter_by(id=case_id, is_active=True).first()
        
        if not case:
            return {'error': 'Case not found'}, 404
        
        if not current_user.is_admin():
            if case.created_by != current_user.id and case.assigned_to != current_user.id:
                return {'error': 'Access denied'}, 403
        
        return {'case': case.to_dict()}, 200
    
    @staticmethod
    def update_case(case_id, data, current_user):
        case = Case.query.filter_by(id=case_id, is_active=True).first()
        
        if not case:
            return {'error': 'Case not found'}, 404
        
        # Check RBAC permissions
        if not RBACManager.can_view_case(current_user, case):
            AuditLogger.log_action(
                current_user.id, "UPDATE_CASE", "CASE", case_id,
                result="FORBIDDEN", details="Cannot view case"
            )
            return {'error': 'Case not found'}, 404
        
        # Determine what fields user can update
        allowed_fields = set()
        
        if RBACManager.can_edit_case(current_user, case):
            # Full edit permissions
            allowed_fields = {'title', 'description', 'priority', 'due_date', 'status'}
            if RBACManager.has_permission(current_user, Permission.ASSIGN_CASES):
                allowed_fields.add('assigned_to')
        elif RBACManager.can_update_case_status(current_user, case):
            # Only status update permissions
            allowed_fields = {'status'}
        
        if not allowed_fields:
            AuditLogger.log_action(
                current_user.id, "UPDATE_CASE", "CASE", case_id,
                result="FORBIDDEN", details="No update permissions"
            )
            return {'error': 'Insufficient permissions to update this case'}, 403
        
        # Check if user is trying to update fields they don't have permission for
        requested_fields = set(data.keys())
        if not requested_fields.issubset(allowed_fields):
            forbidden_fields = requested_fields - allowed_fields
            AuditLogger.log_action(
                current_user.id, "UPDATE_CASE", "CASE", case_id,
                result="FORBIDDEN", 
                details=f"Attempted to update forbidden fields: {forbidden_fields}"
            )
            return {
                'error': f'You can only update these fields: {", ".join(allowed_fields)}',
                'forbidden_fields': list(forbidden_fields)
            }, 403
        
        try:
            # Convert assigned_to from string to int if needed
            if 'assigned_to' in data and data['assigned_to']:
                try:
                    data['assigned_to'] = int(data['assigned_to'])
                except (ValueError, TypeError):
                    data['assigned_to'] = None
            
            # Validate input data
            validated_data = case_update_schema.load(data)
        except Exception as e:
            return {'error': 'Validation failed', 'details': str(e)}, 400
        
        # Handle status transitions
        if 'status' in validated_data:
            new_status = validated_data['status']
            if not case.can_transition_to(new_status):
                return {
                    'error': f'Invalid status transition from {case.status} to {new_status}',
                    'valid_transitions': case.STATUS_TRANSITIONS.get(case.status, [])
                }, 400
            case.status = new_status
        
        # Verify assigned user exists if provided
        if 'assigned_to' in validated_data and validated_data['assigned_to']:
            assigned_user = User.query.get(validated_data['assigned_to'])
            if not assigned_user or not assigned_user.is_active:
                return {'error': 'Assigned user not found or inactive'}, 400
            
            # Ensure regular users can only assign to themselves
            if not RBACManager.has_permission(current_user, Permission.ASSIGN_CASES):
                validated_data['assigned_to'] = current_user.id
        
        # Update other fields
        for field in ['title', 'description', 'priority', 'due_date', 'assigned_to']:
            if field in validated_data:
                setattr(case, field, validated_data[field])
        
        try:
            db.session.commit()
            
            AuditLogger.log_action(
                current_user.id, "UPDATE_CASE", "CASE", case_id,
                result="SUCCESS",
                details=f"Updated fields: {list(validated_data.keys())}"
            )
            
            return {'case': case.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            AuditLogger.log_action(
                current_user.id, "UPDATE_CASE", "CASE", case_id,
                result="ERROR", details=str(e)
            )
            return {'error': 'Failed to update case', 'details': str(e)}, 500
    
    @staticmethod
    def delete_case(case_id, current_user):
        case = Case.query.filter_by(id=case_id, is_active=True).first()
        
        if not case:
            AuditLogger.log_action(
                current_user.id, "DELETE_CASE", "CASE", case_id,
                result="NOT_FOUND", details="Case not found"
            )
            return {'error': 'Case not found'}, 404
        
        # Check RBAC permissions
        if not RBACManager.can_delete_case(current_user, case):
            AuditLogger.log_action(
                current_user.id, "DELETE_CASE", "CASE", case_id,
                result="FORBIDDEN", details="Insufficient delete permissions"
            )
            return {'error': 'Insufficient permissions to delete this case'}, 403
        
        try:
            case_title = case.title  # Store for audit log
            case.soft_delete()
            db.session.commit()
            
            AuditLogger.log_action(
                current_user.id, "DELETE_CASE", "CASE", case_id,
                result="SUCCESS", details=f"Deleted case '{case_title}'"
            )
            
            return {'message': 'Case deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            AuditLogger.log_action(
                current_user.id, "DELETE_CASE", "CASE", case_id,
                result="ERROR", details=str(e)
            )
            return {'error': 'Failed to delete case', 'details': str(e)}, 500