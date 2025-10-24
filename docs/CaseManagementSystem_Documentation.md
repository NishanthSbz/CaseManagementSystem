# Case Management System - Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation Guide](#installation-guide)
4. [Database Schema](#database-schema)
5. [Backend API Documentation](#backend-api-documentation)
6. [Frontend Documentation](#frontend-documentation)
7. [Security Features](#security-features)
8. [User Roles and Permissions](#user-roles-and-permissions)
9. [Development Guide](#development-guide)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Testing Guide](#testing-guide)
12. [Deployment Guide](#deployment-guide)

## 1. Introduction <a name="introduction"></a>

### 1.1 System Overview
The Case Management System (CMS) is a comprehensive web-based application designed to handle case tracking, assignment, and management. It provides a robust platform for organizations to manage cases, assign tasks, track progress, and maintain detailed records of all activities.

### 1.2 Key Features
- User authentication and role-based access control
- Case creation, assignment, and tracking
- Status workflow management
- Audit logging
- Detailed reporting capabilities
- RESTful API architecture
- Responsive web interface

### 1.3 Target Audience
- System Administrators
- Case Managers
- Support Staff
- End Users
- Developers

## 2. System Architecture <a name="system-architecture"></a>

### 2.1 Technology Stack
- **Backend**: Python Flask Framework
- **Frontend**: React.js with Tailwind CSS
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)
- **Container Platform**: Docker
- **Development Environment**: Visual Studio Code

### 2.2 System Components
```
CaseManagementSystem/
├── backend/                 # Flask backend application
├── frontend/               # React frontend application
├── database/               # Database initialization scripts
├── docker-compose.yml      # Docker compose configuration
└── docs/                   # Documentation files
```

### 2.3 Architecture Diagram
```mermaid
graph TD
    A[Client Browser] --> B[React Frontend]
    B --> C[Flask Backend API]
    C --> D[MySQL Database]
    C --> E[JWT Authentication]
    C --> F[RBAC System]
```

## 3. Installation Guide <a name="installation-guide"></a>

### 3.1 Prerequisites
- Docker and Docker Compose
- Git
- Node.js (for local development)
- Python 3.8 or higher (for local development)
- MySQL 8.0 or higher (if not using Docker)

### 3.2 Docker Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CaseManagementSystem.git
   cd CaseManagementSystem
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

### 3.3 Manual Installation

#### Backend Setup
1. Create a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export FLASK_APP=manage.py
   export FLASK_ENV=development
   ```

4. Initialize the database:
   ```bash
   flask init-db
   flask seed-db  # Optional: Add sample data
   ```

#### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with appropriate values
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## 4. Database Schema <a name="database-schema"></a>

### 4.1 Entity Relationship Diagram
```mermaid
erDiagram
    User ||--o{ Case : creates
    User ||--o{ Case : assigned_to
    Case ||--o{ AuditLog : generates
    User ||--o{ AuditLog : performs
```

### 4.2 Table Descriptions

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Cases Table
```sql
CREATE TABLE cases (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('open', 'in_progress', 'closed') DEFAULT 'open',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    due_date DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER NOT NULL,
    assigned_to INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    result VARCHAR(20) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 5. Backend API Documentation <a name="backend-api-documentation"></a>

### 5.1 Authentication Endpoints

#### Register New User
- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "user|admin"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "role": "string"
    },
    "access_token": "string",
    "refresh_token": "string"
  }
  ```

#### Login
- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Login successful",
    "user": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "role": "string"
    },
    "access_token": "string",
    "refresh_token": "string"
  }
  ```

### 5.2 Case Management Endpoints

#### Create Case
- **URL**: `/api/cases`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "priority": "low|medium|high",
    "status": "open|in_progress|closed",
    "due_date": "datetime",
    "assigned_to": "integer"
  }
  ```

#### List Cases
- **URL**: `/api/cases`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `per_page`: integer (default: 10)
  - `status`: string
  - `priority`: string
  - `search`: string

#### Update Case
- **URL**: `/api/cases/<case_id>`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "priority": "string",
    "status": "string",
    "due_date": "datetime",
    "assigned_to": "integer"
  }
  ```

## 6. Frontend Documentation <a name="frontend-documentation"></a>

### 6.1 Component Structure
```
frontend/src/
├── components/           # Reusable components
│   ├── CaseForm.jsx     # Case creation/edit form
│   ├── CaseList.jsx     # List of cases
│   ├── Modal.jsx        # Modal dialog component
│   ├── Navbar.jsx       # Navigation bar
│   └── UI.jsx           # Common UI elements
├── pages/               # Page components
│   ├── Dashboard.jsx    # Main dashboard
│   └── Login.jsx        # Login page
├── store/               # State management
│   ├── authStore.js     # Authentication state
│   └── caseStore.js     # Case management state
└── utils/              # Utility functions
    └── rbac.js         # Role-based access control
```

### 6.2 State Management
The frontend uses a simple state management pattern with React's Context API and hooks.

#### Authentication State
```javascript
const authStore = {
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    // Implementation
  },
  logout: () => {
    // Implementation
  }
};
```

#### Case Management State
```javascript
const caseStore = {
  cases: [],
  loading: false,
  error: null,
  fetchCases: async () => {
    // Implementation
  },
  createCase: async (caseData) => {
    // Implementation
  },
  updateCase: async (caseId, caseData) => {
    // Implementation
  }
};
```

## 7. Security Features <a name="security-features"></a>

### 7.1 Authentication System
- JWT-based authentication
- Token refresh mechanism
- Password hashing using Werkzeug security
- Token blacklisting for logout

### 7.2 Authorization System
The system implements a Role-Based Access Control (RBAC) system with the following features:

#### Permission Levels
```python
class Permission(Enum):
    VIEW_ALL_CASES = "view_all_cases"
    VIEW_OWN_CASES = "view_own_cases"
    CREATE_CASE = "create_case"
    EDIT_OWN_CASES = "edit_own_cases"
    EDIT_ALL_CASES = "edit_all_cases"
    DELETE_OWN_CASES = "delete_own_cases"
    DELETE_ALL_CASES = "delete_all_cases"
    ASSIGN_CASES = "assign_cases"
    VIEW_AUDIT_LOGS = "view_audit_logs"
```

### 7.3 Audit Logging
The system maintains comprehensive audit logs for all actions:
- User actions
- System events
- Authentication attempts
- Data modifications

## 8. User Roles and Permissions <a name="user-roles-and-permissions"></a>

### 8.1 Available Roles
1. **Admin**
   - Full system access
   - User management
   - System configuration
   - Audit log access

2. **User**
   - Case creation
   - View own cases
   - Update assigned cases
   - Basic reporting

### 8.2 Permission Matrix
| Permission           | Admin | User |
|---------------------|-------|------|
| View All Cases      | ✓     | ✗    |
| Create Case         | ✓     | ✓    |
| Edit Any Case       | ✓     | ✗    |
| Edit Own Cases      | ✓     | ✓    |
| Delete Any Case     | ✓     | ✗    |
| Delete Own Cases    | ✓     | ✓    |
| Assign Cases        | ✓     | ✗    |
| View Audit Logs     | ✓     | ✗    |

## 9. Development Guide <a name="development-guide"></a>

### 9.1 Development Environment Setup
1. Install required tools:
   - Visual Studio Code
   - Python 3.8+
   - Node.js 14+
   - Docker Desktop

2. Configure VS Code extensions:
   - Python
   - ESLint
   - Prettier
   - Docker
   - REST Client

### 9.2 Code Style Guidelines

#### Python (Backend)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Document complex functions

Example:
```python
def get_user_cases(user_id: int, status: Optional[str] = None) -> List[Case]:
    """
    Retrieve cases associated with a specific user.
    
    Args:
        user_id: The ID of the user
        status: Optional case status filter
    
    Returns:
        List of Case objects
    """
    query = Case.query.filter_by(created_by=user_id)
    if status:
        query = query.filter_by(status=status)
    return query.all()
```

#### JavaScript (Frontend)
- Use ESLint with Airbnb config
- Use Prettier for formatting
- Use functional components with hooks
- Implement proper error handling

Example:
```javascript
const CaseList = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        setLoading(true);
        const response = await api.getCases();
        setCases(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, []);

  // Component implementation
};
```

### 9.3 Git Workflow
1. Create feature branch from main
2. Implement changes
3. Write/update tests
4. Create pull request
5. Code review
6. Merge to main

## 10. Troubleshooting Guide <a name="troubleshooting-guide"></a>

### 10.1 Common Issues

#### Backend Issues

1. Database Connection Errors
```
Solution:
1. Check database credentials
2. Verify database service is running
3. Check network connectivity
4. Validate connection string
```

2. JWT Token Issues
```
Solution:
1. Verify token expiration
2. Check token secret key
3. Clear browser cookies
4. Re-authenticate
```

#### Frontend Issues

1. API Connection Errors
```
Solution:
1. Verify API endpoint URLs
2. Check CORS configuration
3. Validate authentication tokens
4. Check network connectivity
```

2. State Management Issues
```
Solution:
1. Clear browser cache
2. Reset application state
3. Check React DevTools
4. Verify store updates
```

## 11. Testing Guide <a name="testing-guide"></a>

### 11.1 Backend Testing

#### Unit Tests
```python
def test_user_creation():
    """Test user creation and validation"""
    user = User(
        username="testuser",
        email="test@example.com",
        role="user"
    )
    user.set_password("password123")
    
    assert user.username == "testuser"
    assert user.check_password("password123")
    assert user.role == "user"
```

#### Integration Tests
```python
def test_case_creation_api(client, auth_token):
    """Test case creation through API"""
    response = client.post(
        '/api/cases',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Test Case',
            'description': 'Test Description',
            'priority': 'high'
        }
    )
    
    assert response.status_code == 201
    assert response.json['case']['title'] == 'Test Case'
```

### 11.2 Frontend Testing

#### Component Tests
```javascript
describe('CaseForm Component', () => {
  it('should submit form with valid data', async () => {
    const onSubmit = jest.fn();
    render(<CaseForm onSubmit={onSubmit} />);
    
    await userEvent.type(screen.getByLabelText(/title/i), 'Test Case');
    await userEvent.type(screen.getByLabelText(/description/i), 'Test Description');
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(onSubmit).toHaveBeenCalledWith({
      title: 'Test Case',
      description: 'Test Description'
    });
  });
});
```

## 12. Deployment Guide <a name="deployment-guide"></a>

### 12.1 Production Deployment

#### Docker Deployment
1. Build production images:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Deploy containers:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Initialize database:
```bash
docker-compose exec backend flask init-db
```

#### Manual Deployment

1. Backend Deployment:
```bash
# Set production environment
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://user:pass@host/db

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 manage:app
```

2. Frontend Deployment:
```bash
# Build production bundle
npm run build

# Serve with nginx
cp -r build/* /var/www/html/
```

### 12.2 Configuration Management

#### Environment Variables
```bash
# Backend
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=mysql+pymysql://user:pass@host/db

# Frontend
REACT_APP_API_URL=https://api.example.com
REACT_APP_ENV=production
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 12.3 Monitoring and Maintenance

1. Setup monitoring:
   - Implement health check endpoints
   - Configure logging
   - Set up error tracking
   - Monitor system metrics

2. Backup procedures:
   - Database backups
   - Configuration backups
   - Log rotation
   - Audit trail maintenance

3. Update procedures:
   - Database migrations
   - Code deployments
   - Configuration updates
   - Security patches