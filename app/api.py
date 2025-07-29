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