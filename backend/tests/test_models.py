import pytest
from app.models import User, Case
from app import db

class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self, app):
        """Test creating a new user"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                role='user'
            )
            user.set_password('password123')
            
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.role == 'user'
            assert user.is_active == True
            assert user.check_password('password123')
    
    def test_password_hashing(self, app):
        """Test password hashing functionality"""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('secret')
            
            assert user.password_hash != 'secret'
            assert user.check_password('secret')
            assert not user.check_password('wrong')
    
    def test_admin_role_check(self, app):
        """Test admin role checking"""
        with app.app_context():
            admin = User(username='admin', email='admin@test.com', role='admin')
            user = User(username='user', email='user@test.com', role='user')
            
            assert admin.is_admin()
            assert not user.is_admin()

class TestCaseModel:
    """Test cases for Case model"""
    
    def test_case_creation(self, app, admin_user):
        """Test creating a new case"""
        with app.app_context():
            case = Case(
                title='Test Case',
                description='Test description',
                status='open',
                priority='high',
                created_by=admin_user.id
            )
            
            assert case.title == 'Test Case'
            assert case.status == 'open'
            assert case.priority == 'high'
            assert case.is_active == True
    
    def test_status_transitions(self, app, admin_user):
        """Test case status transition logic"""
        with app.app_context():
            case = Case(
                title='Test Case',
                status='open',
                created_by=admin_user.id
            )
            
            # Valid transitions
            assert case.can_transition_to('in_progress')
            assert case.update_status('in_progress')
            assert case.status == 'in_progress'
            
            assert case.can_transition_to('closed')
            assert case.update_status('closed')
            assert case.status == 'closed'
            
            # Invalid transitions
            assert not case.can_transition_to('open')
            assert not case.update_status('open')
            assert case.status == 'closed'
    
    def test_soft_delete(self, app, admin_user):
        """Test case soft deletion"""
        with app.app_context():
            case = Case(
                title='Test Case',
                created_by=admin_user.id
            )
            db.session.add(case)
            db.session.commit()
            
            assert case.is_active == True
            case.soft_delete()
            assert case.is_active == False