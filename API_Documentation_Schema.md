# API Documentation & Database Schema

## API Endpoints

### Authentication Endpoints

#### POST `/register`
**Description**: Register a new user
**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
**Response**:
```json
{
  "message": "User registered successfully",
  "token": "jwt_token_here"
}
```

#### POST `/login`
**Description**: Authenticate existing user
**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
**Response**:
```json
{
  "message": "Login successful",
  "token": "jwt_token_here"
}
```

### Chat & AI Endpoints

#### POST `/chat`
**Description**: Send a message to the AI assistant
**Headers**: `Authorization: Bearer <token>`
**Request Body**:
```json
{
  "message": "string"
}
```
**Response**:
```json
{
  "answer": "AI response",
  "log_id": 123,
  "sources": ["source1", "source2"]
}
```

#### POST `/feedback`
**Description**: Submit feedback for a response
**Headers**: `Authorization: Bearer <token>`
**Request Body**:
```json
{
  "log_id": 123,
  "helpful": true,
  "feedback_text": "string"
}
```
**Response**:
```json
{
  "message": "Feedback submitted successfully"
}
```

### Data Retrieval Endpoints

#### GET `/conversation/history/{username}`
**Description**: Get user's conversation history
**Headers**: `Authorization: Bearer <token>`
**Query Parameters**:
- `limit`: Number of records to return (default: 100)
**Response**:
```json
{
  "history": [
    {
      "id": 123,
      "user_id": "username",
      "query": "string",
      "response": "string",
      "query_type": "in_scope|out_of_scope|dynamic_data",
      "timestamp": "2025-01-30T10:30:00",
      "processing_time": 2.5,
      "sources": ["source1"],
      "feedback": "{\"helpful\": true, \"feedback_text\": \"\"}"
    }
  ]
}
```

#### GET `/conversation/stats/{username}`
**Description**: Get conversation statistics
**Headers**: `Authorization: Bearer <token>`
**Response**:
```json
{
  "stats": {
    "total_conversations": 50,
    "recent_conversations_24h": 5,
    "query_type_distribution": {
      "in_scope": 30,
      "out_of_scope": 15,
      "dynamic_data": 5
    },
    "feedback_stats": {
      "total_feedback": 20,
      "helpful_feedback": 15,
      "not_helpful_feedback": 5,
      "feedback_rate": 40.0
    }
  }
}
```

### Observability Endpoints

#### GET `/observability/logs`
**Description**: Get system observability logs
**Headers**: `Authorization: Bearer <token>`
**Query Parameters**:
- `limit`: Number of records to return (default: 50)
**Response**:
```json
{
  "logs": [
    {
      "id": 456,
      "user_id": "username",
      "action": "user_query_received",
      "query": "string",
      "timestamp": "2025-01-30T10:30:00",
      "duration": 2.5,
      "result": "success",
      "error": null
    }
  ]
}
