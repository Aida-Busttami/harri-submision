from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserTable(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DeploymentTable(Base):
    __tablename__ = "deployments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False)
    version = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)

class EmployeeTable(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String)
    team = Column(String)
    jira_username = Column(String)

class JiraTicketTable(Base):
    __tablename__ = "jira_tickets"
    id = Column(String, primary_key=True)
    summary = Column(Text, nullable=False)
    assignee = Column(String)
    status = Column(String)
    priority = Column(String)

class LogEntryTable(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sources = Column(Text)
    query_type = Column(String)
    processing_time = Column(Float)
    user_id = Column(String, nullable=True)
    feedback = Column(Text, nullable=True)

class Deployment(BaseModel):
    service: str
    version: str
    date: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)

class Employee(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    team: str
    jira_username: str
    model_config = ConfigDict(from_attributes=True)

class JiraTicket(BaseModel):
    id: str
    summary: str
    assignee: str
    status: str
    priority: str
    model_config = ConfigDict(from_attributes=True)

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's natural language query")
    user_id: Optional[str] = Field(None, description="Optional user identifier for personalization")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer to the user query")
    sources: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    query_type: str = Field(...)
    log_id: Optional[int] = Field(None, description="Database log ID for this response")

class LogEntry(BaseModel):
    id: int
    timestamp: datetime
    query: str
    response: str
    sources: List[str] = Field(default_factory=list)
    query_type: str
    processing_time: float
    user_id: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

