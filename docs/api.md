# Case Management System API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Cases Endpoints

### Create Case
Creates a new case in the system.

**Endpoint:** `POST /cases`

**Authentication:** Required

**Request Body:**
```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (optional)",
  "priority": "string (optional) - enum: low, medium, high - default: medium",
  "status": "string (optional) - enum: open, in_progress, closed - default: open",
  "due_date": "string (optional) - ISO 8601 datetime",
  "assigned_to": "integer (optional) - user ID"
}
```

**Response:** `201 Created`
```json
{
  "case": {
    "id": "integer",
    "title": "string",
    "description": "string",
    "priority": "string",
    "status": "string",
    "due_date": "string",
    "created_by": "integer",
    "assigned_to": "integer",
    "created_at": "string",
    "updated_at": "string"
  }
}
```

### List Cases
Retrieves a paginated list of cases based on query parameters.

**Endpoint:** `GET /cases`

**Authentication:** Required

**Query Parameters:**
- `page` (optional, integer, min: 1, default: 1) - Page number
- `per_page` (optional, integer, min: 1, max: 100, default: 10) - Items per page
- `status` (optional) - Filter by status: open, in_progress, closed
- `priority` (optional) - Filter by priority: low, medium, high
- `search` (optional) - Search in title and description
- `assigned_to` (optional) - Filter by assignee ID
- `created_by` (optional) - Filter by creator ID

**Response:** `200 OK`
```json
{
  "cases": [
    {
      "id": "integer",
      "title": "string",
      "description": "string",
      "priority": "string",
      "status": "string",
      "due_date": "string",
      "created_by": "integer",
      "assigned_to": "integer",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "pagination": {
    "page": "integer",
    "per_page": "integer",
    "total": "integer",
    "pages": "integer",
    "has_next": "boolean",
    "has_prev": "boolean"
  }
}
```

### Update Case
Updates an existing case.

**Endpoint:** `PATCH /cases/{id}`

**Authentication:** Required

**URL Parameters:**
- `id` (required, integer) - Case ID

**Request Body:**
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "priority": "string (optional) - enum: low, medium, high",
  "status": "string (optional) - enum: open, in_progress, closed",
  "due_date": "string (optional) - ISO 8601 datetime",
  "assigned_to": "integer (optional) - user ID"
}
```

**Response:** `200 OK`
```json
{
  "case": {
    "id": "integer",
    "title": "string",
    "description": "string",
    "priority": "string",
    "status": "string",
    "due_date": "string",
    "created_by": "integer",
    "assigned_to": "integer",
    "created_at": "string",
    "updated_at": "string"
  }
}
```

### Delete Case
Deletes a specific case.

**Endpoint:** `DELETE /cases/{id}`

**Authentication:** Required

**URL Parameters:**
- `id` (required, integer) - Case ID

**Response:** `200 OK`
```json
{
  "message": "Case deleted successfully"
}
```

## Error Responses

### Validation Error
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["error message"]
  }
}
```

### Authentication Error
```json
{
  "error": "Unauthorized",
  "message": "Missing or invalid authentication token"
}
```

### Authorization Error
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### Resource Not Found
```json
{
  "error": "Resource not found"
}
```

## Authorization Rules

1. **Regular Users:**
   - Can create cases
   - Can view cases assigned to them
   - Can update cases assigned to them (except closed cases)
   - Can't delete cases

2. **Admin Users:**
   - Can create cases
   - Can view all cases
   - Can update any case
   - Can delete any case
   - Can assign cases to any user