import pytest
from app import create_app, db
from app.models import User, Case
from app.config import TestingConfig

@pytest.fixture
def app():
    """Create application for the tests"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing"""
    with app.app_context():
        user = User(
            username='admin_test',
            email='admin@test.com',
            role='admin'
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def regular_user(app):
    """Create a regular user for testing"""
    with app.app_context():
        user = User(
            username='user_test',
            email='user@test.com',
            role='user'
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def sample_case(app, admin_user):
    """Create a sample case for testing"""
    with app.app_context():
        case = Case(
            title='Test Case',
            description='Test description',
            status='open',
            priority='medium',
            created_by=admin_user.id
        )
        db.session.add(case)
        db.session.commit()
        return case

@pytest.fixture
def auth_headers(client, admin_user):
    """Get authentication headers for admin user"""
    response = client.post('/api/auth/login', json={
        'username': 'admin_test',
        'password': 'test123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def user_auth_headers(client, regular_user):
    """Get authentication headers for regular user"""
    response = client.post('/api/auth/login', json={
        'username': 'user_test',
        'password': 'test123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}