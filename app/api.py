# app/api.py

"""
Simple FastAPI for Harri AI Assistant.
CAUTION: External Email
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import QueryRequest, QueryResponse
from app.query_processor import query_processor
from app.data_service import data_service
from app.config import config

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
    """Get all employees."""
    return data_service.employees

@app.get("/tickets")
async def get_tickets():
    """Get all tickets."""
    return data_service.jira_tickets

@app.get("/deployments")
async def get_deployments():
    """Get all deployments."""
    return data_service.deployments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host=config.API_HOST, port=config.API_PORT, reload=True)

