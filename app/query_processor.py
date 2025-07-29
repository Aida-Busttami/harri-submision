#!/usr/bin/env python3
"""
Query processor module for Harri AI Assistant.
Orchestrates the workflow between knowledge base, data service, and LLM service.
"""

import time
import uuid
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from model import QueryRequest, QueryResponse, LogEntry, LogEntryTable
from knowledge_base import knowledge_base
from data_service import data_service
from llm_service import llm_service
from api_agent import api_agent
from database import SessionLocal
from simple_logs import log_action

class QueryProcessor:
    """Main query processor that orchestrates the AI assistant workflow."""

    def __init__(self):
        """Initialize the query processor."""
        pass

    def process_query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a user query through the complete AI assistant workflow.
        Args:
            request: QueryRequest containing the user's query
        Returns:
            QueryResponse with the AI-generated answer
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        query = request.query

        try:
            # Log user query received
            log_action(query, "user_query_received", duration=0.0)

            logger.info(f"Processing query {query_id}: {request.query}")

            # Step 1: Retrieve relevant knowledge base content
            kb_start = time.time()
            kb_context = self._get_knowledge_base_context(request.query)
            kb_duration = time.time() - kb_start
            
            # Log knowledge base search
            log_action(query, "knowledge_base_search", 
                      result=f"Found {len(kb_context) if kb_context else 0} chars", 
                      duration=kb_duration)

            # Step 2: Use integrated API agent for tool calling and response generation
            agent_start = time.time()
            response = api_agent.process_query_with_tools_and_response(
                query=request.query,
                context=kb_context
            )
            agent_duration = time.time() - agent_start
            
            # Log API agent processing
            log_action(query, "api_agent_processing", 
                      result=f"Generated {len(response.answer)} chars", 
                      duration=agent_duration)
            
            # Note: response_id is not used in the database schema
            
            # Step 3: Log the interaction with sources
            processing_time = time.time() - start_time
            log_id = self._log_interaction(
                query_id=query_id,
                query=query,
                response=response,
                processing_time=processing_time,
                user_id=request.user_id,
                sources_used=response.sources
            )
            
            # Set the log ID in the response for feedback
            if log_id is not None:
                response.log_id = log_id
            
            # Log query completion
            
            log_action(query, "query_completed", 
                      result=f"Success in {processing_time:.2f}s", 
                      duration=processing_time)
            
            logger.info(f"Query {query_id} completed in {processing_time:.2f}s")
            return response

        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log error
            # Log to database for conversation history and analytics (business logic)
            log_action(query, "query_error", error=str(e), duration=processing_time)
            
            # Log to console/logs for debugging and system monitoring (development)
            logger.error(f"Error processing query {query_id}: {e}")
            error_response = QueryResponse(
                answer="I encountered an error while processing your query. Please try again or contact support if the issue persists.",
                query_type="error",
                confidence=0.0,
                sources=[]
            )
            return error_response

    def _get_knowledge_base_context(self, query: str) -> Optional[str]:
        """Retrieve relevant context from the knowledge base."""
        try:
            results = knowledge_base.search(query, top_k=3)
            if not results:
                return None

            context_parts = []
            for result in results:
                content = result["content"]
                metadata = result["metadata"]
                filename = metadata.get("filename", "unknown")
                if len(content) > 500:
                    content = content[:500] + "..."
                context_parts.append(f"[Source: {filename}]\n{content}")
            return "\n\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error retrieving knowledge base context: {e}")
            return None



    def _log_interaction(
        self,
        query_id: str,
        query: str,
        response: QueryResponse,
        processing_time: float,
        user_id: Optional[str] = None,
        sources_used: List[str] = None
    ) -> Optional[int]:
        """Log the interaction to the database. Returns the log ID if successful."""
        try:
            if sources_used is None:
                sources_used = []
                
            db = SessionLocal()
            log_entry = LogEntryTable(
                timestamp=datetime.now(),
                query=query,
                response=response.answer,
                sources=",".join(sources_used),
                query_type=response.query_type,
                processing_time=processing_time,
                user_id=user_id
            )
            db.add(log_entry)
            db.commit()
            log_id = log_entry.id
            db.close()
            return log_id
        except Exception as e:
            logger.error(f"Error logging interaction to database: {e}")
            if 'db' in locals():
                db.close()
            return None



# Global query processor instance
query_processor = QueryProcessor()
