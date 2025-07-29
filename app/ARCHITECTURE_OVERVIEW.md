# Harri AI Assistant - Architecture Overview

## System Architecture

The Harri AI Assistant follows a **layered service-oriented architecture** with clear separation of concerns and **LLM-driven tool calling**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend & API                           │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Streamlit UI  │◄──►│   FastAPI API   │                │
│  │  (3 Tabs)       │    │  (Observability │                │
│  │  - Ask Qs       │    │   Endpoints)    │                │
│  │  - Chat History │    │                 │                │
│  │  - System Logs  │    │                 │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Services                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Query       │ │ API         │ │ Knowledge   │          │
│  │ Processor   │ │ Agent       │ │ Base        │          │
│  │ (Orchestrator)│ (Tool Calling)│ (Document   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Auth        │ │ Data        │ │ Simple      │          │
│  │ Service     │ │ Service     │ │ Observability│          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Storage                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ SQLite DB   │ │ChromaDB     │ │External JSON│          │
│  │ (Logs +     │ │(Document    │ │(Sample Data)│          │
│  │  Observability)│ │ Embeddings) │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Design Choices

### **Backend Framework: FastAPI**
- Fast Python web framework for APIs
- Type checking with Pydantic
- Built-in observability endpoints

### **Database: SQLite**
- Simple file-based database
- No setup required
- Stores users, query logs, and observability data

### **Vector Database: ChromaDB**
- Stores document embeddings
- Enables semantic search
- Runs locally

### **LLM: OpenAI GPT-3.5-turbo**
- Generates AI responses
- **LLM-driven tool calling** - AI decides which tools to use
- **LLM-driven source attribution** - AI identifies its own sources
- Used for intent classification and response generation

### **Frontend: Streamlit**
- Simple web interface with 3 tabs
- Built with Streamlit
- Real-time observability dashboard

## Data Models

### **Core Entities**

```python
# User Management
UserTable(username, password_hash, created_at)

# Business Data
EmployeeTable(id, name, email, role, team, jira_username)
JiraTicketTable(id, summary, assignee, status, priority)
DeploymentTable(id, service, version, date, status)

# Observability & Logging
LogEntryTable(id, response_id, query, response, sources, 
              query_type, processing_time, user_id, feedback)
# Used for both query responses and observability logs
# feedback: stores user ratings and comments on response quality
```

## Database Schema

### **5 Main Tables**

1. **users** - Authentication (username PK, password_hash)
2. **employees** - Team list (id PK, name, email, role, team)
3. **jira_tickets** - Issue tracking (id PK, summary, assignee, status)
4. **deployments** - deployment history (id PK, service, version, date)
5. **logs** - Query tracking with feedback + Observability logs (id PK, response_id UK, query, response, feedback)

### **Key Relationships**

## Component Architecture

### **Query Processor** (`query_processor.py`)
- **Role**: Main orchestrator
- **Responsibilities**: Coordinates all services, gets data, creates responses, saves logs
- **Key Method**: `process_query()`
- **Observability**: Logs user queries, knowledge base searches, API agent processing

### **API Agent** (`api_agent.py`) - **NEW**
- **Role**: LLM-driven tool calling and response generation
- **Responsibilities**: 
  - Uses OpenAI function calling to decide which tools to use
  - Extracts parameters from user queries
  - Calls appropriate tools (get_employees, get_deployments, get_jira_tickets)
  - Generates final responses with **LLM-driven source attribution**
- **Key Methods**: `process_query_with_tools_and_response()`, `_call_tools_with_openai()`, `call_tool()`
- **Observability**: Logs tool calls, executions, and completions

### **LLM Service** (`llm_service.py`)
- **Role**: AI response generation and intent classification
- **Responsibilities**: Understands user questions, builds prompts, generates answers
- **Key Methods**: `process_query()`, `check_query_intent()`, `classify_data_intent()`

### **Knowledge Base** (`knowledge_base.py`)
- **Role**: Document search
- **Responsibilities**: Loads documents, creates search indexes, finds relevant content
- **Key Method**: `search()`

### **Data Service** (`data_service.py`)
- **Role**: Database operations
- **Responsibilities**: Reads and writes data, loads sample data, manages database
- **Key Methods**: `get_employees()`, `get_tickets()`, `get_deployments()`

### **Auth Service** (`auth_service.py`)
- **Role**: User management
- **Responsibilities**: Handles user signup, login, password security, user sessions
- **Key Methods**: `register_user()`, `login_user()`

### **Simple Observability** (`simple_logs.py`) - **NEW**
- **Role**: Simple logging and observability
- **Responsibilities**: Logs all system actions, provides viewing functions
- **Key Methods**: `log_action()`, `get_logs()`, `print_logs()`
- **Features**: Database logging + file logging, JSON-serializable data

## Data Flow

1. **User Input** → Streamlit UI
2. **API Request** → FastAPI endpoint
3. **Query Processing** → Query Processor orchestrates:
   - **Observability**: Logs user query received
   - **Knowledge retrieval** (Knowledge Base) → Logs search
   - **API Agent processing** → LLM-driven tool calling:
     - LLM decides which tools to use
     - LLM extracts parameters
     - Tool execution → Logs tool calls
     - **LLM-driven source attribution** → AI identifies its own sources
   - **Observability**: Logs query completion
4. **Logging** → Database storage (both query responses and observability)
5. **Response** → User interface with enhanced feedback display

## Key Features

- **Natural Language Processing**: LLM-powered query understanding
- **Vector Search**: Semantic document retrieval via ChromaDB
- **Dynamic Data**: Real-time access to employees, tickets, deployments
- **Authentication**: User registration/login with bcrypt
- **LLM-Driven Tool Calling**: AI decides which tools to use and extracts parameters
- **LLM-Driven Source Attribution**: AI identifies and cites its own sources
- **Simple Observability**: Comprehensive logging of all system actions
- **Enhanced UI**: 3-tab interface with system logs and feedback display
- **User Feedback**: Stores user ratings and feedback on responses
- **Color-Coded Logs**: Visual indicators for different action types

## Technology Stack

**Backend**: FastAPI, SQLAlchemy, Pydantic, Uvicorn
**Database**: SQLite, ChromaDB
**AI/ML**: OpenAI GPT-3.5-turbo (with function calling)
**Frontend**: Streamlit (3-tab interface)
**Auth**: Passlib, bcrypt
**Logging**: Simple custom logging + Loguru
**Observability**: Custom simple logging system

## Scalability Path

**Current**: Prototype with SQLite and local ChromaDB
**Production**: PostgreSQL, Redis caching, cloud vector DB, async processing

## Recent Architecture Changes

### **API Agent Integration**
- Replaced manual tool selection with **LLM-driven function calling**
- AI now decides which tools to use based on user queries
- Automatic parameter extraction from natural language

### **LLM-Driven Source Attribution**
- Removed manual source tracking
- AI identifies and cites its own sources in responses
- Sources include both documentation files and API endpoints

### **Simple Observability System**
- Added comprehensive logging of all system actions
- Color-coded log display in UI
- Real-time monitoring of system performance
- Simple database + file logging approach

### **Enhanced UI**
- Added "System Logs" tab for observability
- Enhanced feedback display with structured JSON parsing
- Color-coded action types for better visual understanding 