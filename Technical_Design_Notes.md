# Technical Design & Notes

## Architecture Overview

The Harri Dev Team AI Assistant is built as a **FastAPI backend** with **Streamlit frontend**, following a **microservices-inspired architecture** with clear separation of concerns.

### Core Components

1. **API Layer** (`api.py`)
   - FastAPI application with RESTful endpoints
   - Authentication middleware using JWT tokens
   - Request/response validation with Pydantic models

2. **AI Agent** (`api_agent.py`)
   - LLM-driven tool calling using OpenAI GPT-3.5-turbo
   - Dynamic tool selection based on query intent
   - Context-aware response generation

3. **Data Layer** (`data_service.py`, `database.py`)
   - SQLite database with SQLAlchemy ORM
   - Centralized data access patterns
   - Transaction management and error handling

4. **Knowledge Base** (`chroma_db/`)
   - Vector database for semantic search
   - Document embedding and retrieval
   - Context augmentation for responses

5. **UI Layer** (`ui.py`)
   - Streamlit-based user interface
   - Real-time chat interface
   - Analytics and observability dashboards

## Design Decisions

### 1. Manual Tool Execution vs Automatic
**Decision**: Manual tool execution in `api_agent.py`
**Rationale**: 
- Better control over tool execution flow
- Ability to add custom logic and validation
- Easier debugging and error handling
- More predictable resource usage

### 2. Dual Logging System
**Decision**: Two separate logging mechanisms
**Implementation**:
- `log_action()`: Business/database logging for user actions
- `logger.error()`: System/console logging for technical issues
**Rationale**: Separates business logic from technical debugging

### 3. Conversation Memory Strategy
**Decision**: Database-based conversation history
**Implementation**: `LogEntryTable` stores all interactions
**Rationale**: 
- Persistent across sessions
- Enables analytics and feedback collection
- Supports context-aware responses

### 4. Feedback System Design
**Decision**: Integrated feedback collection with conversation logs
**Implementation**: Feedback stored as JSON in `feedback` column
**Rationale**: 
- Maintains relationship between responses and feedback
- Enables feedback analytics
- Supports continuous improvement

## Observability & Logging

### Logging Strategy
- **Business Logs**: User queries, responses, feedback, tool usage
- **System Logs**: API calls, errors, performance metrics
- **Observability**: Real-time monitoring through `/observability/logs` endpoint

### Metrics Collected
- Query processing time
- Tool usage patterns
- User feedback rates
- Error frequencies
- Response quality indicators

### Monitoring Endpoints
- `/conversation/stats/{username}`: User-specific analytics
- `/observability/logs`: System-wide monitoring
- `/conversation/history/{username}`: Conversation tracking

## Handling Limits & Constraints

### Rate Limiting
- **OpenAI API**: Implemented exponential backoff for rate limits
- **Database**: Connection pooling to handle concurrent requests
- **Memory**: Efficient data structures and cleanup routines

### Token Limits
- **Input Context**: Truncated to fit within model limits
- **Response Length**: Controlled through prompt engineering
- **Tool Results**: Summarized when too large

### Database Constraints
- **SQLite**: File-based database with proper indexing
- **Concurrent Access**: Read-write lock management
- **Data Integrity**: Foreign key constraints and validation

### Memory Management
- **Vector Database**: Efficient embedding storage
- **Session State**: Streamlit session cleanup
- **Large Responses**: Streaming for long outputs

## Assumptions & Limitations

### Technical Assumptions
1. **OpenAI API Availability**: Assumes consistent API access
2. **Local Development**: Designed for single-user/small-team use
3. **Data Privacy**: Assumes local deployment for sensitive data
4. **Network Stability**: Assumes reliable internet for API calls

### Business Assumptions
1. **User Base**: Small development team (not enterprise-scale)
2. **Query Types**: Primarily technical/documentation questions
3. **Response Quality**: Human-in-the-loop validation expected
4. **Data Sources**: Static knowledge base with periodic updates

### Limitations
1. **Scalability**: Not designed for high-concurrency production use
2. **Real-time Updates**: Knowledge base requires manual updates
3. **Multi-language**: Primarily English-focused
4. **Advanced Features**: No advanced NLP features like sentiment analysis

## Security Considerations

### Authentication
- JWT-based token authentication
- Password hashing with bcrypt
- Session management with secure tokens

### Data Protection
- Local database storage (no cloud dependencies)
- Input sanitization and validation
- No sensitive data logging

### API Security
- Request validation with Pydantic
- Error message sanitization
- Rate limiting considerations

## Performance Optimizations

### Database
- Indexed queries for fast retrieval
- Efficient data structures
- Connection pooling

### Caching
- Vector database caching for embeddings
- Session state management
- Response caching for similar queries

### API Optimization
- Async request handling where possible
- Efficient JSON serialization
- Minimal data transfer

## Future Enhancements

### Scalability
- Database migration to PostgreSQL
- Redis caching layer
- Load balancing for multiple instances

### Features
- Real-time collaboration
- Advanced analytics dashboard
- Multi-language support
- Integration with external tools

### Monitoring
- Prometheus metrics
- Grafana dashboards
- Alerting system
- Performance profiling 