"""
Database initialization script for Harri AI Assistant.
Creates tables and loads sample data from JSON files.
"""

import os
import sys
from loguru import logger

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from model import Base, UserTable, EmployeeTable, JiraTicketTable, DeploymentTable
from data_service import DataService

def init_database():
    """Initialize the database with tables and sample data."""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize data service (this will load sample data if tables are empty)
        logger.info("Initializing sample data...")
        data_service = DataService()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database() 