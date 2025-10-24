# Case Management System

A comprehensive system for managing cases, assignments, and workflows with role-based access control.

## Table of Contents
- [Features](#features)
- [Data Model and Design Choices](#data-model-and-design-choices)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Assumptions Made](#assumptions-made)
- [Challenges and Solutions](#challenges-and-solutions)
- [Development](#development)
- [Testing](#testing)

## Features

- User authentication and authorization with JWT
- Role-based access control (Admin and User roles)
- Case management with status tracking
- Case assignment and reassignment
- Priority-based case handling
- Comprehensive audit logging
- RESTful API with documentation
- Responsive React frontend
- Docker containerization

## Technology Stack

### Backend
- Python 3.11 with Flask
- MySQL 8.0 database
- SQLAlchemy ORM
- Flask-JWT-Extended for authentication
- Gunicorn for production server

### Frontend
- React 18 with Vite
- Tailwind CSS for styling
- Zustand for state management
- Axios for API communication

### Infrastructure
- Docker and Docker Compose
- GitHub Actions for CI/CD
- MySQL for data persistence

## Data Model and Design Choices

## Getting Started

### Prerequisites
1. Install [Docker](https://www.docker.com/get-started)
2. Install [Docker Compose](https://docs.docker.com/compose/install/)
3. Git for version control

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/NishanthSbz/CaseManagementSystem.git
   cd CaseManagementSystem
   ```

2. Start the application:
   ```bash
   docker-compose up --build -d
   ```

3. Initialize the database:
   ```bash
   docker-compose exec backend flask db upgrade
   docker-compose exec backend flask seed-db
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/api/docs

### Default Login Credentials

```
Admin User:
- Email: admin@example.com
- Password: admin123

Regular User:
- Email: user1@example.com
- Password: user123
```

## Project Structure

```
CaseManagementSystem/
├── backend/                 # Flask application
│   ├── app/                # Application core
│   │   ├── services/      # Business logic
│   │   ├── models.py      # Database models
│   │   └── routes.py      # API endpoints
│   ├── tests/             # Backend tests
│   └── migrations/        # Database migrations
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/       # Page components
│   │   └── store/       # State management
│   └── public/           # Static assets
├── database/             # Database scripts
├── docs/                # Documentation
└── docker-compose.yml    # Docker configuration

**Design Choices:**
- Implemented status workflow for clear case progression
- Added priority levels for better case management
- Used soft deletion for maintaining historical records
- Included both creator and assignee relationships
- Added due dates for deadline tracking

#### 3. Audit Log Model
```python
class AuditLog:
    id: Integer
    user_id: ForeignKey(User)
    action: String
    resource_type: String
    resource_id: Integer
    result: String
    details: Text
    ip_address: String
    user_agent: Text
    timestamp: DateTime
```

**Design Choices:**
- Comprehensive audit logging for security and compliance
- Stored IP and user agent for security tracking
- Generic resource type/id for flexibility
- Detailed action logging for accountability

### Architecture Decisions

1. **Backend Framework: Flask**
   - Lightweight and flexible
   - Easy to scale
   - Great for RESTful APIs
   - Extensive middleware support

2. **Frontend Framework: React with Tailwind**
   - Component-based architecture
   - Efficient state management
   - Responsive design support
   - Utility-first CSS approach

3. **Database: MySQL**
   - ACID compliance
   - Strong data integrity
   - Excellent documentation
   - Wide community support

4. **Authentication: JWT**
   - Stateless authentication
   - Scalable across services
   - Built-in expiration
   - Secure token-based approach

## Data Model and Design Choices

### Core Models

1. **User Model**
   - Role-based access control
   - Secure password hashing
   - Activity tracking
   - Soft deletion support

2. **Case Model**
   - Priority levels (low, medium, high)
   - Status tracking (open, in_progress, closed)
   - Assignment management
   - Audit trail integration

3. **Audit Log**
   - Comprehensive action tracking
   - User activity monitoring
   - Security event logging
   - Resource access tracking

### Design Decisions

1. **Authentication**
   - JWT-based authentication for stateless scaling
   - Token refresh mechanism
   - Secure password hashing
   - Session management

2. **Database**
   - MySQL for ACID compliance and reliability
   - Migrations for version control
   - Foreign key constraints
   - Indexing for performance

3. **API Design**
   - RESTful architecture
   - Versioned endpoints
   - Comprehensive error handling
   - Rate limiting support

## Assumptions Made

### 1. User Management
- Users can only have one role at a time
- Email addresses are unique across the system
- Passwords must meet minimum security requirements
- Users cannot be permanently deleted (soft deletion only)

### 2. Case Management
- Single assignee per case
- No permanent case deletion
- Required priority and status
- Role-based viewing permissions

### 3. Security
- Authentication required for all routes except login/register
- 24-hour token expiration
- 7-day refresh token validity
- Failed login attempt logging

### 4. Business Logic
- Only admins can assign cases to other users
- Regular users can only view their assigned cases
- Case status changes are logged in audit trail
- Email notifications for case assignments

## Challenges and Solutions

### 1. Complex Permission Management

**Challenge:**
Implementing fine-grained access control for different user roles and resources.

**Solution:**
- Implemented RBAC (Role-Based Access Control)
- Created permission decorators for routes
- Used middleware for permission checking
- Cached permission checks for performance

```python
@require_permission('view_case')
def view_case(case_id):
    case = Case.query.get_or_404(case_id)
    if not current_user.can_view(case):
        abort(403)
    return case_schema.dump(case)
```

### 2. State Management in Frontend

**Challenge:**
Managing complex state across multiple components with different access levels.

**Solution:**
- Implemented centralized state management
- Used React Context for global state
- Created custom hooks for common operations
- Implemented state persistence

```javascript
const useCaseStore = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchCases = async () => {
    setLoading(true);
    try {
      const response = await api.getCases();
      setCases(response.data);
    } finally {
      setLoading(false);
    }
  };

  return { cases, loading, fetchCases };
};
```

### 3. Database Performance

**Challenge:**
Handling large numbers of cases and audit logs efficiently.

**Solution:**
- Implemented database indexing
- Added pagination for large datasets
- Used query optimization
- Implemented caching layer

```python
# Database indexes
Index('idx_cases_status', Case.status)
Index('idx_cases_assigned_to', Case.assigned_to)
Index('idx_audit_logs_timestamp', AuditLog.timestamp)
```

### 4. Real-time Updates

**Challenge:**
Keeping the UI in sync with backend changes.

**Solution:**
- Implemented polling for updates
- Added WebSocket support for real-time notifications
- Used optimistic UI updates
- Implemented retry mechanism for failed requests

## Challenges and Solutions

1. **Cross-Origin Resource Sharing (CORS)**
   - Challenge: Frontend/Backend communication issues
   - Solution: Implemented comprehensive CORS configuration with proper credentials handling

2. **State Management**
   - Challenge: Complex application state
   - Solution: Implemented Zustand for efficient state management

3. **Authentication Flow**
   - Challenge: Secure user sessions
   - Solution: JWT with refresh tokens and secure storage

4. **Database Performance**
   - Challenge: Query optimization
   - Solution: Implemented proper indexing and query optimization

## Development

### Local Development Setup

1. Install dependencies:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

2. Start development servers:
   ```bash
   # Backend
   flask run

   # Frontend
   npm run dev
   ```

### Environment Variables

Create `.env` files in both backend and frontend directories:

```env
# Backend (.env)
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://app_user:app_password@database:3306/case_management
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Frontend (.env)
VITE_API_URL=http://localhost:5000/api
```

## Testing

### Running Tests

1. Backend Tests:
   ```bash
   docker-compose exec backend pytest
   ```

2. Frontend Tests:
   ```bash
   docker-compose exec frontend npm test
   ```

### Code Quality

1. Backend Linting:
   ```bash
   docker-compose exec backend flake8
   docker-compose exec backend black .
   ```

2. Frontend Linting:
   ```bash
   docker-compose exec frontend npm run lint
   ```

## Additional Resources

- [Complete System Documentation](docs/CaseManagementSystem_Documentation.md)
- [API Documentation](docs/api.md)
- [File Structure Documentation](docs/FileStructure_Documentation.md)

### Step 5: Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs

### Default Credentials
```
Admin User:
- Username: admin@example.com
- Password: admin123

Regular User:
- Username: user@example.com
- Password: user123
```

### Running Tests
```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test
```

### Development Commands

#### Backend
```bash
# Create database migration
docker-compose exec backend flask db migrate -m "migration_name"

# Apply migrations
docker-compose exec backend flask db upgrade

# Run linting
docker-compose exec backend flake8
```

#### Frontend
```bash
# Install new dependency
docker-compose exec frontend npm install package_name

# Run linting
docker-compose exec frontend npm run lint

# Build for production
docker-compose exec frontend npm run build
```

## Additional Resources
- [Complete System Documentation](docs/CaseManagementSystem_Documentation.md)
- [File Structure Documentation](docs/FileStructure_Documentation.md)
- [API Documentation](docs/api.md)