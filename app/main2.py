"""
Main entry point for Harri AI Assistant.
Runs the FastAPI server with proper configuration and logging.
"""

import uvicorn
import sys
import os
from loguru import logger

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


debug = True

def setup_logging():
    """Configure logging for the application."""
    # Remove default logger
    logger.remove()

    # Add console logger with custom format
    logger.add(
        sys.stdout,
        format="{time:HH:mm:ss} | {level} | {message}",
        level="DEBUG" if debug else "INFO",
        colorize=True
    )


    # Add file logger for production
    if not debug:
        os.makedirs("logs", exist_ok=True)
        logger.add(
            "logs/harri_ai_assistant.log",
            rotation="10 MB",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO"
        )


def main():
    """Main function to run the FastAPI server."""
    # Setup logging
    setup_logging()


    logger.info("Starting Harri AI Assistant...")

    # Run the server
    uvicorn.run(
        "app.api:app",
        host="localhost",
        port="8000",
        reload=debug
    )


if __name__ == "__main__":
    main()
