#!/usr/bin/env python3
"""
Script to generate sample conversation history for testing memory features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_agent import api_agent
from model import QueryRequest
from query_processor import query_processor
import uuid

def generate_sample_conversation():
    """Generate a sample conversation to test memory features."""
    
    print("🎭 Generating Sample Conversation History")
    print("=" * 50)
    
    # Test user ID
    test_user_id = "demo_user_123"
    
    # Sample conversation flow
    conversation_queries = [
        "Who are the employees?",
        "What are their roles?",
        "Show me the open tickets",
        "What's the deployment process?",
        "How do I set up my dev environment?"
    ]
    
    print(f"Generating conversation for user: {test_user_id}")
    print()
    
    for i, query in enumerate(conversation_queries, 1):
        print(f"Query {i}: {query}")
        
        try:
            # Create a request
            request = QueryRequest(
                query=query,
                user_id=test_user_id
            )
            
            # Process the query
            response = query_processor.process_query(request)
            
            print(f"Response: {response.answer[:100]}...")
            print(f"Query Type: {response.query_type}")
            print(f"Sources: {len(response.sources)} sources")
            print("-" * 40)
            
        except Exception as e:
            print(f"Error processing query: {e}")
            print("-" * 40)
    
    # Test out-of-scope query
    print("Out-of-Scope Query: What's the weather like today?")
    try:
        request = QueryRequest(
            query="What's the weather like today?",
            user_id=test_user_id
        )
        
        response = query_processor.process_query(request)
        print(f"Response: {response.answer[:100]}...")
        print(f"Query Type: {response.query_type}")
        print("-" * 40)
        
    except Exception as e:
        print(f"Error processing out-of-scope query: {e}")
        print("-" * 40)
    
    print("✅ Sample conversation history generated!")
    print("\nNow you can test the conversation context:")
    print("1. Run: python3 test_conversation_context.py")
    print("2. Check the UI for conversation history")
    print("3. Try asking follow-up questions like 'What about their teams?'")

if __name__ == "__main__":
    generate_sample_conversation()
