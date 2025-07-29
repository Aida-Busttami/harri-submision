import uvicorn
import sys
import os
from loguru import logger

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

debug = True

def setup_logging():
    """Configure logging for the application."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:HH:mm:ss} | {level} | {message}",
        level="DEBUG" if debug else "INFO",
        colorize=True
    )
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
    setup_logging()
    logger.info("Starting Harri AI Assistant...")

    # Run uvicorn server for FastAPI
    uvicorn.run(
        "api:app",  # Fixed: use direct import since we're in the app directory
        host="0.0.0.0",
        port=8000,
        reload=debug
    )

if __name__ == "__main__":
    main()
