from functools import wraps
from flask import jsonify, request, current_app, g
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models import User
from app.schemas import user_registration_schema, user_login_schema
from app.rbac import AuditLogger
from app import db

# JWT Blacklist for token revocation
blacklisted_tokens = set()

def auth_required(admin_only=False):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                token = get_jwt()
                if token['jti'] in blacklisted_tokens:
                    AuditLogger.log_action(
                        None, "AUTH_CHECK", "TOKEN",
                        result="REVOKED", details="Token blacklisted"
                    )
                    return jsonify({'error': 'Token has been revoked'}), 401
                
                current_user_id = get_jwt_identity()
                current_user = User.query.get(int(current_user_id))
                
                if not current_user or not current_user.is_active:
                    AuditLogger.log_action(
                        current_user_id, "AUTH_CHECK", "USER",
                        result="INACTIVE", details="User not found or inactive"
                    )
                    return jsonify({'error': 'User not found or inactive'}), 401
                
                g.current_user = current_user
                
                if admin_only and not current_user.is_admin():
                    AuditLogger.log_action(
                        current_user.id, "AUTH_CHECK", "ADMIN",
                        result="FORBIDDEN", details="Admin role required"
                    )
                    return jsonify({'error': 'Admin access required'}), 403
                
                return f(current_user, *args, **kwargs)
                
            except Exception as e:
                print(f"Error in auth decorator: {e}")
                AuditLogger.log_action(
                    None, "AUTH_CHECK", "ERROR",
                    result="ERROR", details=str(e)
                )
                return jsonify({'error': 'Authentication error', 'details': str(e)}), 422
        return decorated_function
    return decorator

def register_user(data):
    try:
        validated_data = user_registration_schema.load(data)
    except Exception as e:
        return {'error': 'Validation failed', 'details': str(e)}, 400
    
    if User.query.filter_by(username=validated_data['username']).first():
        return {'error': 'Username already exists'}, 409
    
    if User.query.filter_by(email=validated_data['email']).first():
        return {'error': 'Email already exists'}, 409
    
    user = User(
        username=validated_data['username'],
        email=validated_data['email'],
        role=validated_data['role']
    )
    user.set_password(validated_data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201
        
    except Exception as e:
        db.session.rollback()
        return {'error': 'Registration failed', 'details': str(e)}, 500

def login_user(data):
    """Authenticate user and return JWT tokens"""
    try:
        # Validate input data
        validated_data = user_login_schema.load(data)
    except Exception as e:
        return {'error': 'Validation failed', 'details': str(e)}, 400
    
    # Find user and verify password
    user = User.query.filter_by(username=validated_data['username']).first()
    
    if not user or not user.check_password(validated_data['password']):
        return {'error': 'Invalid credentials'}, 401
    
    if not user.is_active:
        return {'error': 'Account is inactive'}, 401
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return {
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }, 200

def refresh_token():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user or not user.is_active:
        return {'error': 'User not found or inactive'}, 401
    
    new_token = create_access_token(identity=str(current_user_id))
    return {'access_token': new_token}, 200

def logout_user():
    token = get_jwt()
    blacklisted_tokens.add(token['jti'])
    return {'message': 'Successfully logged out'}, 200

def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return {'error': 'User not found or inactive'}, 401
    
    return {'user': user.to_dict()}, 200