# app/api.py

"""
Simple FastAPI for Harri AI Assistant.
CAUTION: External Email
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from model import QueryRequest, QueryResponse
from query_processor import query_processor
from data_service import data_service
from auth_service import register_user, login_user, get_db
from pydantic import BaseModel
from simple_logs import get_logs
from conversation_context import get_conversation_stats

app = FastAPI(title="Harri AI Assistant")

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Harri AI Assistant"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Main AI query endpoint."""
    try:
        return query_processor.process_query(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees")
async def get_employees():
    """Get all employees from database."""
    return data_service.get_employees()

@app.get("/tickets")
async def get_tickets():
    """Get all tickets from database."""
    return data_service.get_jira_tickets()

@app.get("/deployments")
async def get_deployments():
    """Get all deployments from database."""
    return data_service.get_deployments()

class AuthRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(auth: AuthRequest, db: Session = Depends(get_db)):
    return register_user(auth.username, auth.password, db)

@app.post("/login")
async def login(auth: AuthRequest, db: Session = Depends(get_db)):
    return login_user(auth.username, auth.password, db)

class FeedbackRequest(BaseModel):
    log_id: int
    helpful: bool
    feedback_text: str = ""

@app.post("/feedback")
async def add_feedback(feedback: FeedbackRequest):
    """Add feedback for a response."""
    try:
        success = data_service.add_feedback(
            feedback.log_id, 
            feedback.helpful, 
            feedback.feedback_text
        )
        if success:
            return {"message": "Feedback submitted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Response not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Conversation context endpoints (using existing logs)
@app.get("/conversation/history/{user_id}")
async def get_conversation_history(user_id: str, limit: int = 10):
    """
    Get conversation history for a specific user from existing logs.
    
    Example response:
    {
        "user_id": "test_user",
        "history": [
            {
                "id": 76,
                "query": "Who is on call today?",
                "response": "Today, the on-call engineer is Adam Smith...",
                "sources": ["team_structure.md", "escalation_policy.md"],
                "query_type": "dynamic_data",
                "timestamp": "2025-07-30T00:20:24.973045",
                "processing_time": 4.979432106018066,
                "user_id": "test_user",
                "feedback": null
            }
        ]
    }
    """
    try:
        # Use data_service.get_conversation_history instead of get_logs
        logs = data_service.get_conversation_history(limit, user_id)
        # Convert LogEntry objects to dictionaries for consistency
        history = [log.model_dump() for log in logs]
        return {"user_id": user_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/stats/{user_id}")
async def get_conversation_stats_endpoint(user_id: str):
    """
    Get conversation statistics for a specific user.
    
    Example response:
    {
        "user_id": "test_user",
        "stats": {
            "total_conversations": 1,
            "recent_conversations_24h": 1,
            "query_type_distribution": {
                "dynamic_data": 1
            }
        }
    }
    """
    try:
        stats = get_conversation_stats(user_id)
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple observability endpoints
@app.get("/observability/logs")
async def get_observability_logs(limit: int = 50):
    """Get recent observability logs."""
    try:
        from simple_logs import get_logs
        all_logs = get_logs(limit)
        
        # Filter for actual observability actions (short action names)
        observability_logs = []
        for log in all_logs:
            action = log.get('action', '')
            # Only include logs with short action names (actual observability logs)
            if len(action) < 100 and any(keyword in action.lower() for keyword in ['query', 'tool', 'knowledge', 'api', 'error', 'completed', 'started']):
                observability_logs.append(log)
        
        return {"logs": observability_logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



