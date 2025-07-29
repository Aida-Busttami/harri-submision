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

from app.models import QueryRequest, QueryResponse, LogEntry
from app.knowledge_base import knowledge_base
from app.data_service import data_service
from app.llm_service import llm_service


class QueryProcessor:
    """Main query processor that orchestrates the AI assistant workflow."""

    def __init__(self):
        """Initialize the query processor."""
        self.logs: List[LogEntry] = []

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

        try:
            logger.info(f"Processing query {query_id}: {request.query}")

            # Step 1: Analyze query and determine what data is needed
            query_analysis = self._analyze_query(request.query)

            # Step 2: Retrieve relevant knowledge base content
            kb_context = self._get_knowledge_base_context(request.query)

            # Step 3: Retrieve relevant dynamic data
            dynamic_data = self._get_dynamic_data(query_analysis)

            # Step 4: Generate response using LLM
            response = llm_service.process_query(
                query=request.query,
                context=kb_context,
                dynamic_data=dynamic_data
            )

            # Step 5: Log the interaction
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
                query_type="error"
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

        employee_keywords = ["employee", "team member", "who is", "contact", "email", "on-call", "on call"]
        if any(keyword in query_lower for keyword in employee_keywords):
            analysis["needs_employees"] = True

        # Extract Jira assignee
        assignee_match = re.search(r"my\s+(tickets|issues)", query_lower)
        if assignee_match:
            analysis["jira_assignee"] = "current_user"
        else:
            for emp in data_service.employees:
                if emp.name.lower() in query_lower or emp.jira_username.lower() in query_lower:
                    analysis["jira_assignee"] = emp.jira_username
                    break

        jira_keywords = ["jira", "ticket", "issue", "bug", "task", "open tickets", "assigned"]
        if any(keyword in query_lower for keyword in jira_keywords):
            analysis["needs_jira"] = True

        deployment_keywords = ["deployment", "deploy", "version", "release", "service"]
        if any(keyword in query_lower for keyword in deployment_keywords):
            analysis["needs_deployments"] = True

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

    def _get_dynamic_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant dynamic data based on query analysis."""
        dynamic_data = {}

        if analysis["needs_employees"]:
            dynamic_data["employees"] = data_service.get_employees()

        if analysis["needs_jira"]:
            dynamic_data["jira_tickets"] = data_service.get_open_tickets()

        if analysis["needs_deployments"]:
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
        """Log the interaction for observability."""
        try:
            log_entry = LogEntry(
                timestamp=datetime.now(),
                query=query,
                response=response.answer,
                sources=response.sources,
                query_type=response.query_type,
                processing_time=processing_time,
                user_id=user_id
            )
            self.logs.append(log_entry)
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")

    def add_feedback(self, query_id: str, helpful: bool, feedback_text: Optional[str] = None) -> bool:
        """Add user feedback to a logged interaction."""
        try:
            for log_entry in self.logs:
                log_entry.feedback = {
                    "helpful": helpful,
                    "feedback_text": feedback_text,
                    "timestamp": datetime.now().isoformat()
                }
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return False

    def get_logs(self, limit: int = 100) -> List[LogEntry]:
        """Get recent interaction logs."""
        return self.logs[-limit:] if self.logs else []

    def get_logs_summary(self) -> Dict[str, Any]:
        """Get a summary of interaction logs."""
        if not self.logs:
            return {"total_logs": 0}

        total_logs = len(self.logs)
        query_types = {}
        total_time = 0.0

        for log in self.logs:
            query_types[log.query_type] = query_types.get(log.query_type, 0) + 1
            total_time += log.processing_time

        avg_time = total_time / total_logs
        recent_activity = len([log for log in self.logs if (datetime.now() - log.timestamp).seconds < 3600])

        return {
            "total_logs": total_logs,
            "query_types": query_types,
            "avg_processing_time": avg_time,
            "recent_activity": recent_activity
        }


# Global query processor instance
query_processor = QueryProcessor()
