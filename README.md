# Case Management System

A full-stack web application for managing cases and assignments with role-based access control.

## Documentation
- [Complete System Documentation](docs/CaseManagementSystem_Documentation.md)
- [API Documentation](docs/api.md)
- [File Structure Documentation](docs/FileStructure_Documentation.md)

## Project Structure


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
└── docker-compose.yml    # Docker configuration**Design Choices:**
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

### Core Data Models

```python
class User:
    id: Integer
    username: String
    email: String
    password_hash: String
    role: Enum['admin', 'user']
    is_active: Boolean
    created_at: DateTime
    updated_at: DateTime

class Case:
    id: Integer
    title: String
    description: Text
    status: Enum['open', 'in_progress', 'closed']
    priority: Enum['low', 'medium', 'high']
    due_date: DateTime
    created_by: ForeignKey(User)
    assigned_to: ForeignKey(User)
    created_at: DateTime
    updated_at: DateTime

class AuditLog:
    id: Integer
    user_id: ForeignKey(User)
    action: String
    resource_type: String
    resource_id: Integer
    details: Text
    timestamp: DateTime
```

### Design Decisions

1. **Database Design**
   - Used MySQL for ACID compliance and reliability
   - Implemented soft deletion for data integrity
   - Added timestamps for audit trails
   - Used foreign keys for referential integrity

2. **Authentication System**
   - JWT-based authentication for scalability
   - Refresh token mechanism for better security
   - Role-based access control
   - Password hashing with modern algorithms

3. **API Architecture**
   - RESTful design for consistency
   - Comprehensive error handling
   - Input validation at all endpoints
   - Rate limiting for security

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

python
@require_permission('view_case')
def view_case(case_id):
    case = Case.query.get_or_404(case_id)
    if not current_user.can_view(case):
        abort(403)
    return case_schema.dump(case)


### 2. State Management in Frontend

**Challenge:**
Managing complex state across multiple components with different access levels.

**Solution:**
- Implemented centralized state management
- Used React Context for global state
- Created custom hooks for common operations
- Implemented state persistence

javascript
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


### 3. Database Performance

**Challenge:**
Handling large numbers of cases and audit logs efficiently.

**Solution:**
- Implemented database indexing
- Added pagination for large datasets
- Used query optimization
- Implemented caching layer

python
# Database indexes
Index('idx_cases_status', Case.status)
Index('idx_cases_assigned_to', Case.assigned_to)
Index('idx_audit_logs_timestamp', AuditLog.timestamp)


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

## Quick Start

### Prerequisites
1. **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
2. **Git** - [Download](https://git-scm.com/downloads)

### Running Locally (step by step implementation with Docker)

1. *Clone and Setup Environment*
   bash
   # Clone repository
   git clone https://github.com/NishanthSbz/CaseManagementSystem.git
   cd CaseManagementSystem
   

2. *Backend Setup*
   bash
   # Navigate to backend directory
   cd backend

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

 3. *Environment Setup*
   bash
   # Copy environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Setup environment variables 
   cp .env.example .env 
   

4. *Frontend Setup*
   bash
   # Navigate to frontend directory
   cd ../frontend

   # Install dependencies
   npm install

   # Setup environment variables
   cp .env.example .env
   

5. *Database Setup with Docker*
   bash
   # Start only the database service
   docker-compose up -d database

   # Wait for database to be ready
   docker-compose logs -f database
   

6. *Start Development Servers*

   In one terminal (backend):
   bash
   cd backend
   # Activate virtual environment if not activated
   flask run
   
   In another terminal (frontend):
   bash
   cd frontend
   npm run dev

   *or*

   simply, open the running port(5173) of the frontend image inside the Docker Container.
   

### Default Login Credentials
```
Admin User:
- Email: admin
- Password: admin123

Regular User:
- Email: user1
- Password: user123
```

## Project Overview

### Features
- Role-based user management (Admin/Regular users)
- Case creation and assignment
- Priority-based case handling
- Complete audit logging
- JWT-based authentication

### Technical Stack - Summary
- Backend: Flask (Python)
- Frontend: React with Vite
- Database: MySQL
- Deployment: Docker

### Development Mode
```bash
# Start development services
docker-compose -f docker-compose.yml up -d --build

# Apply database migrations
docker-compose exec backend flask db upgrade
```

### Troubleshooting

1. **Reset Environment**
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f
   ```

3. **Common Issues**
   - Frontend port (5173): Ensure port is available
   - Backend port (5000): Check for conflicts
   - Database port (3307): Verify availability


4. **🛠️ Editor Setup**

This project uses Tailwind CSS. For the best development experience in VS Code, we highly recommend installing the official **[Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)** extension.

This will provide:
* Intelligent autocompletion
* Linting for Tailwind classes
* Syntax highlighting for Tailwind's functions (`@apply`, `@tailwind`, etc.)



