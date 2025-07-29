#!/usr/bin/env python3
"""
API Agent that uses OpenAI function calling to handle tool selection, parameter extraction, and final response generation.
"""

import json
import logging
from typing import Dict, List, Any
from llm_service import llm_service
from model import QueryResponse
from data_service import data_service
from simple_logs import log_action
from conversation_context import get_conversation_context

logger = logging.getLogger(__name__)

class APIAgent:
    """
    Agent that manages API calls using OpenAI function calling and generates final responses.
    Uses chat completion with built-in conversation memory.
    """
    
    def __init__(self):
        """Initialize the API agent."""
        self._last_sources = []
        self.tools = self._define_tools()
        # Store conversation history per user
        self.conversation_history = {}
    
    def _define_tools(self) -> List[Dict]:
        """Define all known tools that the service will use."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_employees",
                    "description": "Get employee information including names, roles, contact info, and on-call status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Employee name to filter by"},
                            "id": {"type": "string", "description": "Employee ID to filter by"},
                            "email": {"type": "string", "description": "Employee email to filter by"},
                            "role": {"type": "string", "description": "Employee role to filter by"},
                            "team": {"type": "string", "description": "Team name to filter by"},
                            "jira_username": {"type": "string", "description": "Jira username to filter by"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_deployments",
                    "description": "Get deployment information including service names, versions, dates, status, and who deployed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string", "description": "Service name to filter by"},
                            "version": {"type": "string", "description": "Version to filter by"},
                            "status": {"type": "string", "description": "Deployment status to filter by"},
                            "date": {"type": "string", "description": "Deployment date to filter by"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_jira_tickets",
                    "description": "Get Jira ticket information including summaries, assignees, status, priority, and project details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Jira ticket ID"},
                            "summary": {"type": "string", "description": "Ticket summary to filter by"},
                            "assignee": {"type": "string", "description": "Assignee name to filter by"},
                            "status": {"type": "string", "description": "Ticket status to filter by"},
                            "priority": {"type": "string", "description": "Ticket priority to filter by"}
                        },
                        "required": []
                    }
                }
            }
        ]
    
    def check_query_intent(self, query: str, user_id: str = "default") -> bool:
        """
        Check if the query intent suits our app using LLM.
        Uses LLM to determine if the query is relevant to Harri's AI Assistant.
        Includes conversation history to maintain consistency.
        
        Returns:
            True if query suits our app, False otherwise
        """
        try:
            if not llm_service.client.api_key:
                # If no API key, default to True (allow all queries)
                return True
            
            # Get conversation context to include previous interactions
            context = get_conversation_context(user_id)
            
            intent_prompt = f"""
            You are an intent classifier for Harri's AI Assistant.
            
            Harri's AI Assistant can help with:
            - Team information and employee details (names, roles, contact info, who is on call, etc.)
            - Jira tickets and project issues  
            - Deployment information
            - Internal documentation and policies
            - Development environment setup
            - Code review processes
            
            IMPORTANT: Consider the conversation history when classifying intent.
            If the user is asking for something that was previously determined to be out of scope,
            maintain consistency and classify it as out of scope.
            
            Conversation History:
            {context if context else "No previous conversation"}
            
            Current Query: "{query}"
            
            Respond with ONLY "YES" if the query suits our app, or "NO" if it doesn't.
            """
            
            response = llm_service.client.chat.completions.create(
                model=llm_service.model,
                messages=[
                    {"role": "system", "content": "You are an intent classifier. Respond only with YES or NO."},
                    {"role": "user", "content": intent_prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().lower()
            llm_result = "yes" in result
            return llm_result
            
        except Exception as e:
            logger.error(f"Error checking intent with LLM: {e}")
            # Default to True if LLM check fails
            return True

    def process_query_with_tools_and_response(self, query: str, context: str = None, user_id: str = "default") -> QueryResponse:
        """
        Process a query using OpenAI function calling and generate final response.
        This is the main method that handles the complete flow with a single LLM call.
        """
        logger.info(f"Processing query with OpenAI function calling: {query}")
        
        try:
            # Step 1: Check if query is in scope using LLM intent classification
            is_in_scope = self.check_query_intent(query, user_id)
            
            if not is_in_scope:
                logger.info(f"Query determined to be out of scope: {query}")
                return self._handle_out_of_scope_query(query, user_id)
            
            # Step 2: Get conversation context from existing logs if not provided
            if context is None:
                context = get_conversation_context(user_id)
            
            # Step 3: Single LLM call that handles both tool calling and response generation
            final_response = self._process_query_with_single_llm_call(query, context)
            
            return final_response
                
        except Exception as e:
            logger.error(f"Error processing query with function calling: {e}")
            return QueryResponse(
                answer=f"I apologize, but I encountered an error processing your query: {str(e)}",
                sources=[],
                confidence=0.0,
                query_type="error"
            )
    
    def _process_query_with_single_llm_call(self, query: str, context: str) -> QueryResponse:
        """Process query with a single LLM call that handles both tool calling and response generation."""
        try:
            # Log single LLM call start
            log_action(query, "single_llm_call_started", duration=0.0)
            
            # Prepare the system prompt with context
            system_prompt = (
                "You are Harri's AI Assistant, a helpful tool for Harri's development team. "
                "You have access to internal documentation, team information, Jira tickets, and deployment data.\n\n"
                "Your role is to:\n"
                "1. Answer questions about Harri's internal processes and policies\n"
                "2. Provide information about team members, Jira tickets, and deployments\n"
                "3. Be helpful and professional in your responses\n"
                "4. Provide clear, direct answers\n\n"
                "CRITICAL: You MUST include a sources footer with ALL sources you used.\n"
                "Format your response exactly like this:\n\n"
                "Your main answer here...\n\n"
                "---\n"
                "Sources: [list ALL sources you used, separated by commas]\n\n"
                "IMPORTANT: You must list EVERY source you used, including:\n"
                "- Documentation files (like escalation_policy.md, team_structure.md)\n"
                "- API endpoints (like /api/employees, /api/deployments, /api/jira-tickets)\n"
                "- Any other data sources mentioned in the context\n\n"
                "You MUST include this footer with ALL sources you used, no exceptions."
            )
            
            # Add context to system prompt if available
            if context:
                system_prompt += f"\n\nRelevant conversation history:\n{context}"
            
            # Create messages for the LLM call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Make the single LLM call with tools
            response = llm_service.client.chat.completions.create(
                model=llm_service.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1000,
                temperature=0.7
            )
            
            # Check if the LLM wants to call any tools
            if response.choices[0].message.tool_calls:
                # Execute tools and get results
                tool_results = {}
                
                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Log individual tool call
                    log_action(query, f"tool_called_{tool_name}", 
                              result=f"Args: {tool_args}", duration=0.0)
                    
                    logger.info(f"LLM called tool {tool_name} with arguments: {tool_args}")
                    
                    # Call the tool with the extracted parameters
                    tool_result = self.call_tool(tool_name, tool_args)
                    tool_results[tool_name] = tool_result
                
                # Add tool results to the conversation and make a second call for final response
                tool_results_text = self._format_tool_results_for_llm(tool_results)
                
                # Add tool results to messages
                messages.append({
                    "role": "assistant", 
                    "content": f"I need to call some tools to get the information you requested.",
                    "tool_calls": response.choices[0].message.tool_calls
                })
                
                # Add tool results
                messages.append({
                    "role": "tool",
                    "content": tool_results_text,
                    "tool_call_id": response.choices[0].message.tool_calls[0].id
                })
                
                # Generate final response with tool results
                final_response = llm_service.client.chat.completions.create(
                    model=llm_service.model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                answer = final_response.choices[0].message.content
                query_type = "dynamic_data"
                
            else:
                # No tools were called - this is static knowledge
                log_action(query, "no_tools_called", 
                          result="Static knowledge only", duration=0.0)
                logger.info("LLM did not call any tools - treating as static knowledge")
                
                answer = response.choices[0].message.content
                query_type = "static_knowledge"
            
            # Extract sources from footer and clean up the answer
            import re
            sources_from_response = []
            clean_answer = answer
            
            # Look for footer pattern: "---\nSources:
            footer_patterns = [
                r'Sources:\s*(.+)'
            ]
            
            for pattern in footer_patterns:
                footer_match = re.search(pattern, answer, re.DOTALL | re.IGNORECASE)
                if footer_match:
                    # Extract sources from footer
                    sources_text = footer_match.group(1).strip()
                    # Split by comma and clean up each source
                    sources_from_response = [s.strip() for s in sources_text.split(',') if s.strip()]
                    # Remove footer from answer
                    clean_answer = re.sub(pattern, '', answer, flags=re.DOTALL | re.IGNORECASE).strip()
                    break
            
            # Use only the sources that the LLM mentioned in its footer
            self._last_sources = sources_from_response
            
            # Log single LLM call completion
            log_action(query, "single_llm_call_completed", 
                      result=f"Query type: {query_type}", duration=0.0)
            
            return QueryResponse(
                answer=clean_answer,  # Use clean answer without footer
                sources=sources_from_response,  # Include extracted sources
                confidence=0.8,
                query_type=query_type
            )
            
        except Exception as e:
            # Log single LLM call error
            log_action(query, "single_llm_call_error", error=str(e), duration=0.0)
            logger.error(f"Error in single LLM call: {e}")
            # Set sources to empty for error cases
            self._last_sources = []
            return QueryResponse(
                answer="I apologize, but I encountered an error generating a response. Please try again.",
                sources=[],
                confidence=0.0,
                query_type="error"
            )
    
    def _format_tool_results_for_llm(self, tool_results: Dict[str, Any]) -> str:
        """Format tool results for the LLM to understand."""
        formatted_results = []
        
        for tool_name, result in tool_results.items():
            if tool_name == "get_employees" and "employees" in result:
                formatted_results.append(f"Employee data (from /api/employees endpoint):\n{json.dumps(result['employees'], indent=2)}")
            elif tool_name == "get_deployments" and "deployments" in result:
                formatted_results.append(f"Deployment data (from /api/deployments endpoint):\n{json.dumps(result['deployments'], indent=2)}")
            elif tool_name == "get_jira_tickets" and "jira_tickets" in result:
                formatted_results.append(f"Jira ticket data (from /api/jira-tickets endpoint):\n{json.dumps(result['jira_tickets'], indent=2)}")
        
        return "\n\n".join(formatted_results)
    
    def _handle_out_of_scope_query(self, query: str, user_id: str = "default") -> QueryResponse:
        """Handle queries that are outside the system's scope."""
        try:
            # Get conversation context from existing logs for better out-of-scope responses
            conversation_context = get_conversation_context(user_id)
            
            # Let the LLM generate a proper out of scope response
            messages = [
                {
                    "role": "system", 
                    "content": (
                        "You are Harri's AI Assistant. Your scope is limited to Harri's internal data: "
                        "employees, deployments, Jira tickets, and internal documentation. "
                        "The user's query is outside your capabilities. "
                        "Politely explain this and suggest what you can help with instead. "
                        "If the user refers to something from previous conversation, explicitly mention what they're referring to."
                    )
                }
            ]
            
            # Add conversation context if available
            if conversation_context:
                messages.append({
                    "role": "system",
                    "content": f"Previous conversation context:\n{conversation_context}"
                })
            
            messages.append({
                "role": "user", 
                "content": f"Query: {query}"
            })
            
            response = llm_service.client.chat.completions.create(
                model=llm_service.model,
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return QueryResponse(
                answer=answer,
                sources=[],
                confidence=0.9,
                query_type="out_of_scope"
            )
            
        except Exception as e:
            logger.error(f"Error handling out of scope query: {e}")
            # Set sources to empty for error cases
            self._last_sources = []
            return QueryResponse(
                answer="I apologize, but this query is outside my scope. I can help you with information about Harri's employees, deployments, Jira tickets, and internal documentation. Please ask me about these topics instead.",
                sources=[],
                confidence=0.8,
                query_type="out_of_scope"
            )
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the specific tool with parameters using real database data.
        
        Note: While OpenAI's function calling API allows LLMs to call tools directly,
        this manual execution approach is preferred for our use case because:
        1. Security: LLM doesn't have direct database access
        2. Control: We maintain full control over tool execution and data access
        3. Logging: We can track tool executions for observability
        4. Custom Logic: Our tools have specific business logic for Harri's data
        5. Error Handling: We can handle database errors gracefully
        
        The LLM decides which tools to call, but we execute them manually for better
        security and control over our internal data.
        """
        try:
            # Log tool execution start
            log_action(f"Tool: {tool_name}", f"tool_execution_{tool_name}", 
                      result=f"Parameters: {parameters}", duration=0.0)
            
            if tool_name == "get_employees":
                result = self._get_employees_from_db(parameters)
            elif tool_name == "get_deployments":
                result = self._get_deployments_from_db(parameters)
            elif tool_name == "get_jira_tickets":
                result = self._get_jira_tickets_from_db(parameters)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            # Log tool execution completion
            log_action(f"Tool: {tool_name}", f"tool_execution_{tool_name}_completed", 
                      result=f"Returned {len(str(result))} chars", duration=0.0)
            
            return result
            
        except Exception as e:
            # Log tool execution error
            log_action(f"Tool: {tool_name}", f"tool_execution_{tool_name}_error", 
                      error=str(e), duration=0.0)
            return {"error": str(e)}
    
    def _get_employees_from_db(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get employees from database with optional filtering based on parameters."""
        try:
            employees = data_service.get_employees()
            employees_data = [emp.model_dump() for emp in employees]
            
            # Apply filters if parameters are provided
            if parameters:
                filtered_employees = []
                for emp in employees_data:
                    # Check if employee matches all provided filters
                    matches = True
                    for key, value in parameters.items():
                        if value and key in emp:
                            # Case-insensitive partial matching for string fields
                            if isinstance(emp[key], str) and isinstance(value, str):
                                if value.lower() not in emp[key].lower():
                                    matches = False
                                    break
                            # Exact matching for non-string fields
                            elif emp[key] != value:
                                matches = False
                                break
                    
                    if matches:
                        filtered_employees.append(emp)
                
                employees_data = filtered_employees
            
            return {"employees": employees_data}
        except Exception as e:
            logger.error(f"Error getting employees from database: {e}")
            return {"employees": []}
    
    def _get_deployments_from_db(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get deployments from database with optional filtering based on parameters."""
        try:
            deployments = data_service.get_deployments()
            deployments_data = [dep.model_dump() for dep in deployments]
            
            # Apply filters if parameters are provided
            if parameters:
                filtered_deployments = []
                for dep in deployments_data:
                    # Check if deployment matches all provided filters
                    matches = True
                    for key, value in parameters.items():
                        if value and key in dep:
                            # Case-insensitive partial matching for string fields
                            if isinstance(dep[key], str) and isinstance(value, str):
                                if value.lower() not in dep[key].lower():
                                    matches = False
                                    break
                            # Exact matching for non-string fields
                            elif dep[key] != value:
                                matches = False
                                break
                    
                    if matches:
                        filtered_deployments.append(dep)
                
                deployments_data = filtered_deployments
            
            return {"deployments": deployments_data}
        except Exception as e:
            logger.error(f"Error getting deployments from database: {e}")
            return {"deployments": []}
    
    def _get_jira_tickets_from_db(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get Jira tickets from database with optional filtering based on parameters."""
        try:
            tickets = data_service.get_jira_tickets()
            tickets_data = [ticket.model_dump() for ticket in tickets]
            
            # Apply filters if parameters are provided
            if parameters:
                filtered_tickets = []
                for ticket in tickets_data:
                    # Check if ticket matches all provided filters
                    matches = True
                    for key, value in parameters.items():
                        if value and key in ticket:
                            # Case-insensitive partial matching for string fields
                            if isinstance(ticket[key], str) and isinstance(value, str):
                                if value.lower() not in ticket[key].lower():
                                    matches = False
                                    break
                            # Exact matching for non-string fields
                            elif ticket[key] != value:
                                matches = False
                                break
                    
                    if matches:
                        filtered_tickets.append(ticket)
                
                tickets_data = filtered_tickets
            
            return {"jira_tickets": tickets_data}
        except Exception as e:
            logger.error(f"Error getting Jira tickets from database: {e}")
            return {"jira_tickets": []}

    def get_last_sources(self) -> List[str]:
        """Get the sources used in the last response generation."""
        return getattr(self, '_last_sources', [])

# Global API agent instance
api_agent = APIAgent() 