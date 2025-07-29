"""
Query processor module for Harri AI Assistant.
Orchestrates the workflow between knowledge base, data service, and LLM service.
"""

import time
import uuid
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from model import QueryRequest, QueryResponse, LogEntry, LogEntryTable
from knowledge_base import knowledge_base
from data_service import data_service
from llm_service import llm_service
from database import SessionLocal


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
            QueryResponse with the AI-generated answerx
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())

        try:
            logger.info(f"Processing query {query_id}: {request.query}")

            # Step 1: Check if query intent suits our app
            if not llm_service.check_query_intent(request.query):
                intent_response = QueryResponse(
                    answer="I apologize, but this query doesn't seem to suit my capabilities. I can help you with team information, Jira tickets, deployments, and internal documentation. Please try asking something related to Harri's development team.",
                    sources=[],
                    confidence=0.9,
                    query_type="intent_mismatch",
                    response_id=query_id
                )
                
                processing_time = time.time() - start_time
                self._log_interaction(
                    query_id=query_id,
                    query=request.query,
                    response=intent_response,
                    processing_time=processing_time,
                    user_id=request.user_id
                )
                return intent_response

            # Step 2: Determine what data types are needed using LLM
            data_types = llm_service.classify_data_intent(request.query)

            # Step 3: Retrieve relevant knowledge base content
            kb_context = self._get_knowledge_base_context(request.query)

            # Step 4: Retrieve relevant dynamic data
            dynamic_data = self._get_dynamic_data(data_types)

            # Step 5: Generate response using LLM
            response = llm_service.process_query(
                query=request.query,
                context=kb_context,
                dynamic_data=dynamic_data
            )
            # Add response_id to the response
            response.response_id = query_id

            # Step 6: Log the interaction
            processing_time = time.time() - start_time
            self._log_interaction(
                query_id=query_id,
                query=request.query,
                response=response,
                processing_time=processing_time,
                user_id=request.user_id
            )
            logger.info(f"Query {query_id} completed in {processing_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"Error processing query {query_id}: {e}")
            error_response = QueryResponse(
                answer="I apologize, but I encountered an error processing your query. Please try again or contact support.",
                sources=[],
                confidence=0.0,
                query_type="error",
                response_id=query_id
            )

            processing_time = time.time() - start_time
            self._log_interaction(
                query_id=query_id,
                query=request.query,
                response=error_response,
                processing_time=processing_time,
                user_id=request.user_id
            )
            return error_response

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query to determine what type of data is needed.
        Returns:
            Dictionary with query analysis results
        """
        query_lower = query.lower()
        analysis = {
            "needs_employees": False,
            "needs_jira": False,
            "needs_deployments": False,
            "needs_knowledge": True,
            "jira_assignee": None,
            "service_name": None
        }

        # Check for employee-related queries
        employee_keywords = ["employee", "team member", "staff", "who is", "contact"]
        if any(keyword in query_lower for keyword in employee_keywords):
            analysis["needs_employees"] = True

        # Check for Jira ticket queries
        jira_keywords = ["ticket", "issue", "bug", "task", "jira"]
        if any(keyword in query_lower for keyword in jira_keywords):
            analysis["needs_jira"] = True

        # Check for deployment queries
        deployment_keywords = ["deployment", "deploy", "release", "version"]
        if any(keyword in query_lower for keyword in deployment_keywords):
            analysis["needs_deployments"] = True

        # Extract Jira assignee from query
        assignee_match = re.search(r"assigned to (\w+)", query_lower)
        if assignee_match:
            analysis["jira_assignee"] = assignee_match.group(1)

        # Extract service name from query
        services = ["payments", "onboarding", "frontend", "backend"]
        for service in services:
            if service in query_lower:
                analysis["service_name"] = service
                break

        return analysis

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

    def _get_dynamic_data(self, data_types: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant dynamic data based on LLM classification."""
        dynamic_data = {}

        if data_types.get("employees", False):
            dynamic_data["employees"] = data_service.get_employees()

        if data_types.get("jira", False):
            dynamic_data["jira_tickets"] = data_service.get_open_tickets()

        if data_types.get("deployments", False):
            dynamic_data["deployments"] = data_service.get_recent_deployments()

        return dynamic_data

    def _log_interaction(
        self,
        query_id: str,
        query: str,
        response: QueryResponse,
        processing_time: float,
        user_id: Optional[str] = None
    ) -> None:
        """Log the interaction to the database."""
        try:
            db = SessionLocal()
            log_entry = LogEntryTable(
                response_id=response.response_id,
                timestamp=datetime.now(),
                query=query,
                response=response.answer,
                sources=",".join(response.sources) if response.sources else "",
                query_type=response.query_type,
                processing_time=processing_time,
                user_id=user_id
            )
            db.add(log_entry)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error logging interaction to database: {e}")

    def add_feedback(self, response_id: str, helpful: bool, feedback_text: str = "") -> bool:
        """Add feedback for a response by updating existing entry."""
        try:
            db = SessionLocal()
            # Find the log entry by response_id
            log_entry = db.query(LogEntryTable).filter(
                LogEntryTable.response_id == response_id
            ).first()
            
            if log_entry:
                feedback_data = {
                    "helpful": helpful,
                    "feedback_text": feedback_text,
                    "timestamp": datetime.now().isoformat()
                }
                log_entry.feedback = str(feedback_data)
                db.commit()
                db.close()
                return True
            else:
                db.close()
                return False
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return False

    def get_logs(self, limit: int = 100) -> List[LogEntry]:
        """Get recent interaction logs from database."""
        try:
            db = SessionLocal()
            log_entries = db.query(LogEntryTable).order_by(
                LogEntryTable.timestamp.desc()
            ).limit(limit).all()
            
            logs = []
            for entry in log_entries:
                sources = entry.sources.split(",") if entry.sources else []
                feedback = None
                if entry.feedback:
                    try:
                        import ast
                        feedback = ast.literal_eval(entry.feedback)
                    except:
                        feedback = {"text": entry.feedback}
                
                log_entry = LogEntry(
                    response_id=entry.response_id,
                    timestamp=entry.timestamp,
                    query=entry.query,
                    response=entry.response,
                    sources=sources,
                    query_type=entry.query_type,
                    processing_time=entry.processing_time,
                    user_id=entry.user_id,
                    feedback=feedback
                )
                logs.append(log_entry)
            
            db.close()
            return logs
        except Exception as e:
            logger.error(f"Error retrieving logs from database: {e}")
            return []

# Global query processor instance
query_processor = QueryProcessor()
