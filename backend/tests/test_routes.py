import pytest
import json

class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_user_registration(self, client):
        """Test user registration endpoint"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123',
            'role': 'user'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
    
    def test_duplicate_username_registration(self, client, admin_user):
        """Test registration with duplicate username"""
        response = client.post('/api/auth/register', json={
            'username': 'admin_test',
            'email': 'different@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
    
    def test_user_login(self, client, admin_user):
        """Test user login endpoint"""
        response = client.post('/api/auth/login', json={
            'username': 'admin_test',
            'password': 'test123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_invalid_login(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrong'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

class TestCaseRoutes:
    """Test case management endpoints"""
    
    def test_create_case(self, client, auth_headers):
        """Test case creation endpoint"""
        response = client.post('/api/cases', 
            json={
                'title': 'New Test Case',
                'description': 'Test description',
                'priority': 'high'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'case' in data
        assert data['case']['title'] == 'New Test Case'
    
    def test_get_cases(self, client, auth_headers, sample_case):
        """Test getting cases with pagination"""
        response = client.get('/api/cases?page=1&per_page=10', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'cases' in data
        assert 'pagination' in data
    
    def test_update_case(self, client, auth_headers, sample_case):
        """Test case update endpoint"""
        response = client.patch(f'/api/cases/{sample_case.id}',
            json={
                'title': 'Updated Title',
                'status': 'in_progress'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['case']['title'] == 'Updated Title'
        assert data['case']['status'] == 'in_progress'
    
    def test_invalid_status_transition(self, client, auth_headers, sample_case):
        """Test invalid status transition"""
        response = client.patch(f'/api/cases/{sample_case.id}',
            json={'status': 'closed'},  # can't go directly from open to closed
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_delete_case(self, client, auth_headers, sample_case):
        """Test case deletion endpoint"""
        response = client.delete(f'/api/cases/{sample_case.id}',
                               headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_unauthorized_access(self, client, sample_case):
        """Test accessing cases without authentication"""
        response = client.get('/api/cases')
        assert response.status_code == 401
    
    def test_access_control(self, client, user_auth_headers, admin_user):
        """Test user access control for cases"""
        # Regular user tries to access admin's case
        response = client.get('/api/cases', headers=user_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        # Should return empty list since no cases belong to regular user
        assert len(data['cases']) == 0

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test API health check"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'