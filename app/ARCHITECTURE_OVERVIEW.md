# Harri AI Assistant - Architecture Overview

## System Architecture

The Harri AI Assistant follows a **layered service-oriented architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend & API                           │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Streamlit UI  │◄──►│   FastAPI API   │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Services                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Query       │ │ LLM         │ │ Knowledge   │          │
│  │ Processor   │ │ Service     │ │ Base        │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐                          │
│  │ Auth        │ │ Data        │                          │
│  │ Service     │ │ Service     │                          │
│  └─────────────┘ └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Storage                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ SQLite DB   │ │ChromaDB     │ │External JSON│          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Design Choices

### **Backend Framework: FastAPI**
- Fast Python web framework for APIs
- Type checking with Pydantic

### **Database: SQLite**
- Simple file-based database
- No setup required
- Stores users and query logs containing feedback.

### **Vector Database: ChromaDB**
- Stores document embeddings
- Enables semantic search
- Runs locally

### **LLM: OpenAI GPT-3.5-turbo**
- Generates AI responses
- Understands natural language
- Used for intent classification

### **Frontend: Streamlit**
- Simple web interface
- Built with Streamlit

## Data Models

### **Core Entities**

```python
# User Management
UserTable(username, password_hash, created_at)

# Business Data
EmployeeTable(id, name, email, role, team, jira_username)
JiraTicketTable(id, summary, assignee, status, priority)
DeploymentTable(id, service, version, date, status)

# Observability
LogEntryTable(id, response_id, query, response, sources, 
              query_type, processing_time, user_id, feedback)
# feedback: stores user ratings and comments on response quality
```


## Database Schema

### **5 Main Tables**

1. **users** - Authentication (username PK, password_hash)
2. **employees** - Team list (id PK, name, email, role, team)
3. **jira_tickets** - Issue tracking (id PK, summary, assignee, status)
4. **deployments** - deployment history (id PK, service, version, date)
5. **logs** - Query tracking with feedback (id PK, response_id UK, query, response, feedback)

### **Key Relationships**



## Component Architecture

### **Query Processor** (`query_processor.py`)
- **Role**: Main orchestrator
- **Responsibilities**: data retrieval, response generation, logging
- **Key Method**: `process_query()`

### **LLM Service** (`llm_service.py`)
- **Role**: AI response generation
- **Responsibilities**: Intent checking, prompt building, response generation
- **Key Methods**: `process_query()`, `check_query_intent()`, `classify_data_intent()`

### **Knowledge Base** (`knowledge_base.py`)
- **Role**: Document search
- **Responsibilities**: Document loading, vector indexing, semantic search
- **Key Method**: `search()`

### **Data Service** (`data_service.py`)
- **Role**: Database operations
- **Responsibilities**: CRUD operations, data initialization, sample data loading
- **Key Methods**: `get_employees()`, `get_tickets()`, `get_deployments()`

### **Auth Service** (`auth_service.py`)
- **Role**: User management
- **Responsibilities**: Registration, login, password hashing, session management
- **Key Methods**: `register_user()`, `login_user()`

## Data Flow

1. **User Input** → Streamlit UI
2. **API Request** → FastAPI endpoint
3. **Query Processing** → Query Processor orchestrates:
   - Intent validation (LLM Service)
   - Knowledge retrieval (Knowledge Base)
   - Data fetching (Data Service)
   - Response generation (LLM Service)
4. **Logging** → Database storage
5. **Response** → User interface

## Key Features

- **Natural Language Processing**: LLM-powered query understanding
- **Vector Search**: Semantic document retrieval via ChromaDB
- **Dynamic Data**: Real-time access to employees, tickets, deployments
- **Authentication**: User registration/login with bcrypt
- **Observability**: Comprehensive logging and feedback collection
- **User Feedback**: Stores user ratings and feedback on responses
- **Source Attribution**: All responses cite their data sources

## Technology Stack

**Backend**: FastAPI, SQLAlchemy, Pydantic, Uvicorn
**Database**: SQLite, ChromaDB
**AI/ML**: OpenAI GPT-3.5-turbo
**Frontend**: Streamlit
**Auth**: Passlib, bcrypt
**Logging**: Loguru

## Scalability Path

**Current**: Prototype with SQLite and local ChromaDB
**Production**: PostgreSQL, Redis caching, cloud vector DB, async processing 