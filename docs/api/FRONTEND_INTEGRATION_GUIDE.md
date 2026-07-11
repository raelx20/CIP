# CIP Frontend Integration Guide

## Overview

The Constituency Intelligence Platform (CIP) backend provides a REST API for citizens, MPs, officers, and admins.

## Authentication

### Single Login Screen

All users authenticate through the same login endpoint. After login, the frontend routes based on the user's role.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "citizen",
    "is_active": true
  }
}
```

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User",
  "role": "citizen"
}
```

### Using the Token

Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## User Roles

| Role | View | Access |
|------|------|--------|
| citizen | Chat interface | Submit complaints, track status |
| mp | Dashboard | View issues, priorities, hotspots |
| officer | Review queue | Review submissions, make decisions |
| admin | Full dashboard | Manage everything |

## Citizen Endpoints

### Submit Complaint

```http
POST /api/v1/citizen/submissions
Content-Type: application/json

{
  "content": "The road near my house has many potholes...",
  "source_modality": "text",
  "language": "en",
  "gps_permission_granted": true,
  "sender_latitude": 20.2961,
  "sender_longitude": 85.8245
}
```

### Chat with AI

```http
POST /api/v1/citizen/chat
Content-Type: application/json

{
  "role": "citizen",
  "content": "I want to report a water problem",
  "detected_language": "en"
}
```

### Get Chat History

```http
GET /api/v1/citizen/chat/history/{session_id}
```

## Admin/MP Endpoints

### Dashboard Overview

```http
GET /api/v1/admin/dashboard
```

Response:
```json
{
  "total_submissions": 1250,
  "pending_review": 45,
  "active_clusters": 89,
  "high_priority": 12,
  "issues_by_category": [
    {"category": "water", "count": 320},
    {"category": "road", "count": 280}
  ]
}
```

### List Issues

```http
GET /api/v1/admin/issues?category=water&skip=0&limit=100
```

### Get Issue Detail

```http
GET /api/v1/admin/issues/{issue_id}
```

### Get Priority Rankings

```http
GET /api/v1/admin/priorities?min_level=high
```

### Query Copilot

```http
POST /api/v1/admin/copilot
Content-Type: application/json

{
  "query": "What are the highest-priority water issues?",
  "constituency": "Bhubaneswar"
}
```

## GPS Permission Handling

When the frontend requests GPS permission:

1. **Permission Granted**: Send coordinates in the submission
2. **Permission Denied**: Continue without coordinates, mark as unavailable
3. **GPS Mismatch**: System treats as one weighted signal, not automatic fraud

## Multilingual Chat

The AI responds in the detected language of the user:

- User sends in Odia → AI responds in Odia
- User sends in Hindi → AI responds in Hindi
- User sends in English → AI responds in English
- Code-mixed input → AI responds in natural blend

## Pagination

All list endpoints support:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 100, max: 1000)

## Error Handling

All errors return:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "request_id": "uuid"
  }
}
```

## CORS Configuration

Default allowed origins:
- `http://localhost:3000` (Next.js dev)

## Health Check

```http
GET /api/v1/system/health
GET /api/v1/system/ready
```

## OpenAPI Documentation

Visit `/docs` for interactive API documentation.
