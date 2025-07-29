from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic import BaseModel, EmailStr
class Deployment(BaseModel):
    service: str
    version: str
    date: datetime
    status: str

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    team: str
    jira_username: str

    class Config:
        orm_mode = True
class Task(BaseModel):
    id: str
    summary: str
    assignee: str
    status: str
    priority: str
    

class QueryRequest(BaseModel):
    """Request model for user queries to the AI assistant."""
    query: str = Field(..., description="User's natural language query")
    user_id: Optional[str] = Field(None, description="Optional user identifier for personalization")

class QueryResponse(BaseModel):
    """Response model for AI assistant answers."""
    answer: str = Field(..., description="AI-generated answer to the user query")
    sources: List[str] = Field(default_factory=list, description="List of sources used to generate the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the answer (0.0 to 1.0)")
    query_type: str = Field(..., description="Type of query (static_knowledge, dynamic_data, out_of_scope)")

    
class FeedbackRequest(BaseModel):
    """Request model for user feedback on AI responses."""
    query_id: str = Field(..., description="Unique identifier for the query")
    helpful: bool = Field(..., description="Whether the response was helpful")
    feedback_text: Optional[str] = Field(None, description="Optional detailed feedback")
class LogEntry(BaseModel):
    """Model for logging user interactions and system actions."""
    timestamp: datetime = Field(..., description="Timestamp of the interaction")
    query: str = Field(..., description="User query")
    response: str = Field(..., description="AI response")
    sources: List[str] = Field(default_factory=list, description="Sources used for answer generation")
    query_type: str = Field(..., description="Detected type of query")
    processing_time: float = Field(..., description="Time taken to generate the response in seconds")
    user_id: Optional[str] = Field(None, description="Optional ID of the user")
    feedback: Optional[Dict[str, Any]] = Field(None, description="Optional feedback data")
