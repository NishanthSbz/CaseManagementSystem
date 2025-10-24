# Case Management System - File Structure Documentation

## Project Root Files

### Configuration Files
- `docker-compose.yml`
  - Main Docker Compose configuration
  - Defines production services: backend, frontend, and database
  - Sets up networking and volume mappings
  - Configures environment variables for production

- `docker-compose.dev.yml`
  - Development Docker Compose configuration
  - Includes hot-reload for frontend and backend
  - Mounts source code directories for development
  - Sets up development-specific environment variables

### Testing Files
- `test_assignment_fixes.py`
  - Tests for case assignment bug fixes
  - Validates case reassignment logic
  - Ensures proper handling of edge cases in assignments

- `test_assignment_logic.py`
  - Core tests for case assignment logic
  - Validates business rules for case assignments
  - Tests load balancing and priority handling

- `test_auth_validation.py`
  - Authentication validation tests
  - Verifies token handling and validation
  - Tests user authentication flows

## Backend Directory (`/backend`)

### Root Configuration
- `Dockerfile`
  - Backend container configuration
  - Sets up Python environment
  - Installs dependencies
  - Configures Flask application

- `manage.py`
  - Flask application entry point
  - CLI commands for database management
  - Development server configuration
  - Application factory implementation

- `requirements.txt`
  - Python package dependencies
  - Specifies version requirements
  - Production and development dependencies

### Application Core (`/backend/app`)

- `__init__.py`
  - Flask application factory
  - Blueprint registration
  - Extension initialization
  - Configuration loading

- `auth.py`
  - Authentication implementation
  - JWT token handling
  - Login/logout logic
  - Password hashing utilities

- `authorization.py`
  - Authorization logic
  - Permission checking
  - Access control helpers
  - Role validation

- `config.py`
  - Application configuration
  - Environment variables
  - Feature flags
  - Security settings

- `models.py`
  - SQLAlchemy database models
  - Table relationships
  - Model methods and properties
  - Data validation logic

- `rbac.py`
  - Role-Based Access Control system
  - Permission definitions
  - Role hierarchies
  - Access control decorators

- `routes.py`
  - API endpoint definitions
  - Request handling
  - Response formatting
  - Route middleware

- `schemas.py`
  - Marshmallow serialization schemas
  - Request/response validation
  - Data transformation rules
  - Field definitions

### Services (`/backend/app/services`)

- `case_service.py`
  - Case management business logic
  - CRUD operations for cases
  - Case workflow handling
  - Business rule implementation

- `simplified_case_service.py`
  - Simplified case operations
  - Basic CRUD functionality
  - Streamlined workflow
  - Reduced complexity operations

### Database (`/backend/migrations`)

- `alembic.ini`
  - Alembic migration configuration
  - Database connection settings
  - Migration environment setup

- `env.py`
  - Migration environment setup
  - Database connection handling
  - Migration context configuration

- `versions/`
  - Database migration files
  - Schema version control
  - Data migration scripts
  - `ecf2bae06e87_initial_migration.py`: Initial database schema

### Tests (`/backend/tests`)

- `conftest.py`
  - PyTest configuration
  - Test fixtures
  - Test database setup
  - Mock object definitions

- `test_authorization.py`
  - Authorization system tests
  - Permission checking tests
  - Role assignment validation
  - Access control verification

- `test_models.py`
  - Database model tests
  - Relationship validation
  - Model method tests
  - Data integrity checks

- `test_routes.py`
  - API endpoint tests
  - Request/response validation
  - Integration tests
  - Error handling tests

## Database Directory (`/database`)

- `init.sql`
  - Initial database setup
  - Table creation scripts
  - Default data insertion
  - Database user setup

## Frontend Directory (`/frontend`)

### Configuration Files
- `Dockerfile`
  - Production frontend container
  - Node.js environment setup
  - Build process configuration
  - Nginx server setup

- `Dockerfile.dev`
  - Development frontend container
  - Hot-reload configuration
  - Development dependencies
  - Volume mounting

- `package.json`
  - NPM package configuration
  - Dependencies list
  - Script definitions
  - Project metadata

- `postcss.config.cjs`
  - PostCSS configuration
  - CSS processing rules
  - Plugin configuration
  - CSS optimization settings

- `tailwind.config.cjs`
  - Tailwind CSS configuration
  - Theme customization
  - Utility classes
  - Plugin settings

- `vite.config.js`
  - Vite bundler configuration
  - Build settings
  - Development server
  - Plugin configuration

### Source Files (`/frontend/src`)

- `App.jsx`
  - Root React component
  - Route configuration
  - Global state providers
  - Layout structure

- `index.css`
  - Global CSS styles
  - Tailwind imports
  - Custom CSS variables
  - Base styles

- `main.jsx`
  - Application entry point
  - React DOM rendering
  - Global providers
  - Initial setup

#### API (`/frontend/src/api`)

- `api.js`
  - API client configuration
  - Axios setup
  - Request interceptors
  - Response handling

- `index.js`
  - API endpoint exports
  - Service organization
  - API utilities
  - Type definitions

#### Components (`/frontend/src/components`)

- `CaseForm.jsx`
  - Case creation/editing form
  - Form validation
  - Data submission
  - Error handling

- `CaseList.jsx`
  - Case listing component
  - Filtering and sorting
  - Pagination
  - List item rendering

- `Modal.jsx`
  - Reusable modal component
  - Dialog management
  - Transition effects
  - Accessibility features

- `Navbar.jsx`
  - Navigation component
  - User menu
  - Navigation links
  - Responsive design

- `ProtectedRoute.jsx`
  - Route protection wrapper
  - Authentication checking
  - Role-based access
  - Redirect logic

- `UI.jsx`
  - Common UI components
  - Buttons, inputs, etc.
  - Styling utilities
  - Shared components

#### Pages (`/frontend/src/pages`)

- `Dashboard.jsx`
  - Main dashboard page
  - Case overview
  - Statistics display
  - Action buttons

- `Login.jsx`
  - Login page component
  - Authentication form
  - Error handling
  - Redirect logic

#### Store (`/frontend/src/store`)

- `authStore.js`
  - Authentication state management
  - User session handling
  - Login/logout actions
  - Token management

- `caseStore.js`
  - Case data management
  - CRUD operations
  - Case state
  - Filter management

#### Utils (`/frontend/src/utils`)

- `rbac.js`
  - Frontend role checking
  - Permission utilities
  - Access control helpers
  - Role constants

## Documentation (`/docs`)

- `CaseManagementSystem_Documentation.md`
  - Comprehensive system documentation
  - Setup instructions
  - API documentation
  - Development guides

- `FileStructure_Documentation.md` (this file)
  - Detailed file structure
  - File purposes
  - Component relationships
  - Configuration details