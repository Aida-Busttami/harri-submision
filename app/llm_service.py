"""
LLM service module for Harri AI Assistant.
Handles interactions with OpenAI API for generating responses.
"""

import os
import json
import time
import re
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger
from openai import OpenAI

from model import QueryResponse


class LLMService:
    """Service class for handling LLM interactions and query processing."""

    def __init__(self):
        """Initialize the LLM service with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key or "")
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000

    def process_query(
        self,
        query: str,
        context: Optional[str] = None,
        dynamic_data: Optional[Dict[str, Any]] = None
    ) -> QueryResponse:
        """
        Process a user query and generate a response using the LLM.

        Args:
            query: User's natural language query
            context: Relevant context from knowledge base
            dynamic_data: Dynamic data from JSON sources

        Returns:
            QueryResponse with answer, sources, confidence, and query type
        """
        start_time = time.time()
        try:
            query_type, prompt = self._build_prompt(query, context, dynamic_data)
            response = self._generate_response(prompt)
            sources = self._extract_sources(context, dynamic_data)
            processing_time = time.time() - start_time

            logger.info(f"Query processed in {processing_time:.2f}s - Type: {query_type}")

            return QueryResponse(
                answer=response,
                sources=sources,
                confidence=0.8,  # Default confidence
                query_type=query_type
            )
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                answer="I apologize, but I encountered an error processing your query. Please try again or contact support.",
                sources=[],
                confidence=0.0,
                query_type="error"
            )

    def _build_prompt(
        self,
        query: str,
        context: Optional[str] = None,
        dynamic_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Build a prompt for the LLM based on query type and available data.

        Returns:
            Tuple of (query_type, prompt)
        """
        system_prompt = (
            "You are Harri's AI Assistant, a helpful tool for Harri's development team. "
            "You have access to internal documentation, team information, Jira tickets, and deployment data.\n\n"
            "Your role is to:\n"
            "1. Answer questions about Harri's internal processes and policies\n"
            "2. Provide information about team members, Jira tickets, and deployments\n"
            "3. Be helpful and professional in your responses\n"
            "4. Always cite your sources when providing information\n"
            "5. Clearly indicate when a request is outside your scope\n\n"
            "When citing sources, use the format: [Source: filename.md] or [Source: employees.json] etc."
        )

        query_type = "static_knowledge"
        context_parts = []

        if context:
            context_parts.append(f"Relevant documentation:\n{context}")

        if dynamic_data:
            query_type = "dynamic_data"
            if "employees" in dynamic_data:
                context_parts.append(f"Team information:\n{dynamic_data['employees']}")
            if "jira_tickets" in dynamic_data:
                context_parts.append(f"Jira tickets:\n{dynamic_data['jira_tickets']}")
            if "deployments" in dynamic_data:
                context_parts.append(f"Deployment information:\n{dynamic_data['deployments']}")

        user_prompt = f"User query: {query}\n\n"
        if context_parts:
            user_prompt += "Available information:\n" + "\n\n".join(context_parts) + "\n\n"
        user_prompt += "Please provide a helpful response based on the available information."

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        return query_type, full_prompt

    def _generate_response(self, prompt: str) -> str:
        """Generate a response using the OpenAI API."""
        try:
            if not self.client.api_key:
                return "I'm currently in demo mode and don't have access to the OpenAI API. Please set the OPENAI_API_KEY environment variable to enable full functionality."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Harri's AI Assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error generating a response. Please try again."

    def check_query_intent(self, query: str) -> bool:
        """
        Check if the query intent suits our app using LLM.
        Uses LLM to determine if the query is relevant to Harri's AI Assistant.
        
        Returns:
            True if query suits our app, False otherwise
        """
        try:
            if not self.client.api_key:
                # If no API key, default to True (allow all queries)
                return True
            
            intent_prompt = f"""
            You are an intent classifier for Harri's AI Assistant.
            
            Harri's AI Assistant can help with:
            - Team information and employee details
            - Jira tickets and project issues  
            - Deployment information
            - Internal documentation and policies
            - Development environment setup
            - Code review processes
            
            Query: "{query}"
            
            Respond with ONLY "YES" if the query suits our app, or "NO" if it doesn't.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intent classifier. Respond only with YES or NO."},
                    {"role": "user", "content": intent_prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().lower()
            return "yes" in result
            
        except Exception as e:
            logger.error(f"Error checking intent with LLM: {e}")
            # Default to True if LLM check fails
            return True

    def _extract_sources(
        self,
        context: Optional[str] = None,
        dynamic_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Extract source information from context and dynamic data."""
        sources = []
        
        if context:
            # Extract source filenames from context
            source_matches = re.findall(r"\[Source: ([^\]]+)\]", context)
            sources.extend(source_matches)
        
        if dynamic_data:
            if "employees" in dynamic_data:
                sources.append("employees.json")
            if "jira_tickets" in dynamic_data:
                sources.append("jira_tickets.json")
            if "deployments" in dynamic_data:
                sources.append("deployments.json")
        
        return list(set(sources))  # Remove duplicates


# Global LLM service instance
llm_service = LLMService()
