from flask import request
from sqlalchemy import and_, or_
from app.models import Case, User
from app.schemas import case_create_schema, case_update_schema, case_query_schema
from app.authorization import get_accessible_cases_query, authorize_case_access
from app import db

class SimplifiedCaseService:
    @staticmethod
    def create_case(data, current_user):
        try:
            validated_data = case_create_schema.load(data)
        except Exception as e:
            return {'error': 'Validation failed', 'details': str(e)}, 400
        
        if validated_data.get('assigned_to'):
            assigned_user = User.query.get(validated_data['assigned_to'])
            if not assigned_user or not assigned_user.is_active:
                return {'error': 'Assigned user not found or inactive'}, 400
        else:
            validated_data['assigned_to'] = current_user.id
        
        case = Case(
            title=validated_data['title'],
            description=validated_data['description'],
            priority=validated_data['priority'],
            status=validated_data.get('status', 'open'),
            due_date=validated_data.get('due_date'),
            created_by=current_user.id,
            assigned_to=validated_data['assigned_to']
        )
        
        try:
            db.session.add(case)
            db.session.commit()
            return {'case': case.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to create case', 'details': str(e)}, 500
    
    @staticmethod
    def get_cases(query_params, current_user):
        # Parse query parameters with safe defaults
        try:
            page = max(1, int(query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
            
        try:
            per_page = min(max(1, int(query_params.get('per_page', 10))), 100)
        except (ValueError, TypeError):
            per_page = 10
        
        # Build base query with role-based filtering
        query = get_accessible_cases_query(current_user)
        
        # Apply additional filters
        if query_params.get('status') in ['open', 'in_progress', 'closed']:
            query = query.filter(Case.status == query_params['status'])
        
        if query_params.get('priority') in ['low', 'medium', 'high']:
            query = query.filter(Case.priority == query_params['priority'])
        
        if query_params.get('search'):
            search_term = f"%{query_params['search']}%"
            query = query.filter(
                or_(
                    Case.title.ilike(search_term),
                    Case.description.ilike(search_term)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Case.created_at.desc())
        
        # Paginate results
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
        
        return {'case': case.to_dict()}, 200
    
    @staticmethod
    def update_case(case_id, data, current_user):
        case = Case.query.filter_by(id=case_id, is_active=True).first()
        
        if not case:
            return {'error': 'Case not found'}, 404
        
        try:
            validated_data = case_update_schema.load(data)
        except Exception as e:
            return {'error': 'Validation failed', 'details': str(e)}, 400
        
        if 'status' in validated_data:
            new_status = validated_data['status']
            if not case.can_transition_to(new_status):
                return {
                    'error': f'Invalid status transition from {case.status} to {new_status}',
                    'valid_transitions': case.STATUS_TRANSITIONS.get(case.status, [])
                }, 400
            case.status = new_status
        
        if 'assigned_to' in validated_data and validated_data['assigned_to']:
            assigned_user = User.query.get(validated_data['assigned_to'])
            if not assigned_user or not assigned_user.is_active:
                return {'error': 'Assigned user not found or inactive'}, 400
        
        for field in ['title', 'description', 'priority', 'due_date', 'assigned_to']:
            if field in validated_data:
                setattr(case, field, validated_data[field])
        
        try:
            db.session.commit()
            return {'case': case.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to update case', 'details': str(e)}, 500
    
    @staticmethod
    def delete_case(case_id, current_user):
        case = Case.query.filter_by(id=case_id, is_active=True).first()
        
        if not case:
            return {'error': 'Case not found'}, 404
        
        try:
            case.soft_delete()
            db.session.commit()
            return {'message': 'Case deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to delete case', 'details': str(e)}, 500