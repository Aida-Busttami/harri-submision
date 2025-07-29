"""
LLM service module for Harri AI Assistant.
Handles interactions with OpenAI API for generating responses.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMService:
    """Service class for handling LLM interactions and query processing."""

    def __init__(self):
        """Initialize the LLM service with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key or "")
        self.model = "gpt-3.5-turbo-16k"  # Better context window for conversation memory
        self.max_tokens = 1000


# Global LLM service instance
llm_service = LLMService()
