# Case Management System

A production-ready full-stack web application for managing cases with simplified admin/user authorization, built with Flask (backend) and React (frontend).

## 🔐 Authorization & Business Rules

This application implements a **simplified authorization model** with clear business rules for data protection:

### **Roles**
- **Admin**: Full system access
- **User**: Limited access to owned resources

### **Access Control Rules**

#### **Case Management Authorization:**
1. **Admin**: Can create, read, update, and delete **any case**
2. **User**: 
   - Can **create** cases (auto-assigned to themselves if no assignee specified)
   - Can **read** cases they own OR are assigned to
   - Can **update/delete** only cases they own (not just assigned)
3. **Closed Case Protection**: Users cannot delete or modify cases that have status `"closed"`. Only admins can modify closed cases.

#### **API Endpoint Authorization:**
- `POST /cases` - Both admin and user can create cases (auto-assigns to creator)
- `GET /cases` - Admin sees all cases, users see owned + assigned cases  
- `GET /cases/{id}` - Admin can view any case, users can view owned + assigned cases
- `PATCH /cases/{id}` - Admin can update any case, users can only update owned non-closed cases
- `DELETE /cases/{id}` - Admin can delete any case, users can only delete owned non-closed cases

#### **Security Features:**
- **Server-side enforcement**: All authorization checks happen on the backend
- **403 Unauthorized responses**: Returns `{"error": "Unauthorized access"}` for violations
- **Clean structure**: Uses `authorize_case_access()` utility function for consistent checks
- **JWT Authentication**: Payload includes `{id, role}` for the logged-in user

### **Database Schema**
Cases have an `owner_id` field (implemented as `created_by`) that identifies which user created/owns the case.

## 🚀 Quick Start Guide

### Prerequisites
- **Docker Desktop** (Recommended - easiest way)
- OR: Node.js 18+ and Python 3.11+ for local development

### Option 1: Run with Docker (Recommended)

```bash
# 1. Navigate to project directory
cd "d:\CaseManagementSystem"

# 2. Start all services
docker-compose up --build

# 3. Wait for services to start (about 2-3 minutes)
# You'll see logs from database, backend, and frontend

# 4. Access the application:
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000/api
# Health Check: http://localhost:5000/api/health
```

### Demo Credentials
```
Admin User:
- Username: admin
- Password: admin123

Regular User:
- Username: user1  
- Password: user123
```

### Option 2: Local Development Setup

#### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional - defaults work)
$env:FLASK_ENV="development"
$env:DATABASE_URL="mysql+pymysql://root:password@localhost/case_management"

# Run backend (starts on port 5000)
python manage.py
```

#### Frontend Setup (New Terminal)
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server (starts on port 5173)
npm run dev
```

#### Database Setup (If running locally)
```bash
# Install MySQL and create database
mysql -u root -p
CREATE DATABASE case_management;
exit

# Run migrations (from backend directory)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed-db
```

## 🎯 What You'll See

### 1. Login Page
- Clean authentication interface
- Demo credentials provided
- Registration option available

### 2. Dashboard
- Case list with pagination
- Filtering by status and priority
- Search functionality
- Create new case button

### 3. Case Management
- Create/Edit case modal
- Status workflow enforcement
- Priority levels
- Due date scheduling
- Assignment capabilities

### 4. Admin Features (admin user only)
- View all users
- Access all cases
- Full administrative control

## 🔧 Troubleshooting

### Docker Issues
```bash
# If containers fail to start, try:
docker-compose down -v
docker-compose up --build

# Check container status:
docker-compose ps

# View logs:
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database
```

### Common Issues
1. **Port conflicts**: Make sure ports 3306, 5000, 5173 are available
2. **Database connection**: Wait for MySQL to fully initialize
3. **Frontend blank page**: Check if backend is running and healthy

### Health Checks
- Backend: http://localhost:5000/api/health
- Frontend: http://localhost:5173
- Database: Check with `docker-compose logs database`

## 📦 API Testing

### Using curl or Postman:
```bash
# Health check
curl http://localhost:5000/api/health

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Get cases (with token)
curl -X GET http://localhost:5000/api/cases \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎉 Success Indicators

You know everything is working when:
1. ✅ Docker shows all 3 containers running
2. ✅ Frontend loads at http://localhost:5173
3. ✅ You can login with demo credentials
4. ✅ You can create and manage cases
5. ✅ API responds at http://localhost:5000/api/health

## 🔄 Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

A production-ready full-stack web application for managing cases with role-based access control, built with Flask (backend) and React (frontend).

## 🚀 Features

### Core Functionality
- **Complete CRUD Operations** for case management
- **JWT-based Authentication** with access and refresh tokens
- **Role-based Access Control** (Admin/User roles)
- **Case Status Workflow** with enforced transitions (Open → In Progress → Closed)
- **Pagination and Filtering** for case listings
- **Soft Delete** functionality for data preservation

### Technical Highlights
- **RESTful API** with consistent JSON responses
- **Production-grade Flask** application with modular architecture
- **Modern React SPA** with Vite and Tailwind CSS
- **Responsive Design** with mobile-first approach
- **State Management** using Zustand
- **Form Validation** with React Hook Form
- **Real-time Notifications** using React Toastify
- **Containerized Deployment** with Docker Compose
- **CI/CD Pipeline** with GitHub Actions
- **Comprehensive Testing** with pytest and critical path coverage

## 📋 Data Model

### User Model
```python
- id: Primary key
- username: Unique username (3-80 chars)
- email: Unique email address
- password_hash: Bcrypt hashed password
- role: Enum ['admin', 'user']
- is_active: Boolean for soft delete
- created_at: Timestamp
- updated_at: Timestamp
```

### Case Model
```python
- id: Primary key
- title: Case title (1-200 chars)
- description: Detailed description (optional)
- status: Enum ['open', 'in_progress', 'closed']
- priority: Enum ['low', 'medium', 'high']
- due_date: Optional deadline
- is_active: Boolean for soft delete
- created_at: Timestamp
- updated_at: Timestamp
- created_by: Foreign key to User
- assigned_to: Foreign key to User (optional)
```

## 🏗️ Architecture

### Backend (Flask)
```
backend/
├── app/
│   ├── __init__.py          # App factory and extensions
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # API endpoints
│   ├── schemas.py           # Marshmallow validation schemas
│   ├── auth.py              # JWT authentication logic
│   ├── config.py            # Configuration classes
│   └── services/
│       └── case_service.py  # Business logic layer
├── tests/                   # Comprehensive test suite
├── migrations/              # Database migrations
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── manage.py               # Application runner
```

### Frontend (React)
```
frontend/
├── src/
│   ├── api/                # API client and endpoints
│   ├── components/         # Reusable UI components
│   ├── pages/              # Route components
│   ├── store/              # Zustand state management
│   ├── utils/              # Utility functions
│   ├── App.jsx             # Main application component
│   └── main.jsx            # Application entry point
├── public/                 # Static assets
├── Dockerfile             # Container configuration
└── package.json           # Node.js dependencies
```

## 🔒 Business Rules

### Status Transitions
Cases follow a strict workflow:
- **Open** → **In Progress** ✅
- **In Progress** → **Closed** ✅
- Direct **Open** → **Closed** ❌
- Reverse transitions ❌

### Access Control
- **Regular Users**: Can only view and edit cases they created or are assigned to
- **Admin Users**: Full access to all cases and user management
- **Authentication Required**: All endpoints except health check require valid JWT

### Data Validation
- **Title**: Required, 1-200 characters
- **Due Date**: Must be in the future if provided
- **Email**: Valid email format required for registration
- **Password**: Minimum 6 characters
- **Username**: 3-80 characters, unique

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Run with Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd CaseManagementSystem

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000/api
# Database: localhost:3306
```

### Demo Credentials
```
Admin User:
- Username: admin
- Password: admin123

Regular User:
- Username: user1
- Password: user123
```

### Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export DATABASE_URL=mysql+pymysql://root:password@localhost/case_management

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed-db

# Run development server
python manage.py
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_routes.py -v
```

### Frontend Linting
```bash
cd frontend

# Lint code
npm run lint

# Fix lint issues
npm run lint:fix
```

## 📦 API Endpoints

### Authentication
```
POST /api/auth/register     # User registration
POST /api/auth/login        # User login
POST /api/auth/refresh      # Refresh access token
POST /api/auth/logout       # Logout (blacklist token)
GET  /api/auth/me          # Get current user info
```

### Case Management
```
GET    /api/cases              # List cases (paginated, filtered)
POST   /api/cases              # Create new case
GET    /api/cases/{id}         # Get specific case
PATCH  /api/cases/{id}         # Update case
DELETE /api/cases/{id}         # Soft delete case
```

### Admin Only
```
GET /api/admin/users           # List all users
GET /api/admin/cases           # List all cases (including inactive)
```

### Query Parameters (GET /api/cases)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)
- `status`: Filter by status
- `priority`: Filter by priority
- `assigned_to`: Filter by assigned user ID
- `created_by`: Filter by creator user ID

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
DATABASE_URL=mysql+pymysql://user:password@host:port/database
FLASK_ENV=production|development|testing
CORS_ORIGINS=http://localhost:5173,http://frontend:5173
```

#### Frontend
```bash
VITE_API_URL=http://localhost:5000/api
```

## 🚀 Deployment

### Production Deployment
1. **Environment Setup**: Configure production environment variables
2. **Database**: Set up production MySQL database
3. **SSL/TLS**: Configure HTTPS certificates
4. **Reverse Proxy**: Set up Nginx or similar
5. **Monitoring**: Implement logging and monitoring

### Docker Compose Production
```bash
# Use production environment file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/React
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## 📊 Project Status

✅ **Completed Features:**
- Complete CRUD operations
- JWT authentication and authorization
- Role-based access control
- Status workflow validation
- Pagination and filtering
- Responsive UI design
- Docker containerization
- CI/CD pipeline
- Comprehensive testing

🚧 **Potential Enhancements:**
- Email notifications
- File attachments
- Audit logging
- Advanced search
- Dashboard analytics
- Export functionality
- Real-time updates with WebSockets
- Mobile app