"""
Simple data service for Harri AI Assistant.
Loads data from SQLite database and provides basic data access.
"""

import json
import os
from datetime import datetime
from loguru import logger
from typing import List, Optional
from sqlalchemy.orm import Session

from database import SessionLocal
from model import Employee, JiraTicket, Deployment, EmployeeTable, JiraTicketTable, DeploymentTable, LogEntry, LogEntryTable



class DataService:
    """Simple service to load and serve data from database."""

    def __init__(self):
        """Initialize database with sample data if empty."""
        self._init_database()

    def _init_database(self):
        """Initialize database with sample data from JSON files if empty."""
        db = SessionLocal()
        try:
            # Check if database is empty by counting employees
            employee_count = db.query(EmployeeTable).count()
            
            if employee_count == 0:
                logger.info("Database is empty. Loading sample data...")
                self._load_sample_data(db)
                logger.info("Database initialized successfully")
            else:
                logger.info(f"Database already contains {employee_count} employees. Skipping sample data loading.")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            db.close()

    def _load_sample_data(self, db: Session):
        """Load sample data from JSON files into database."""
        try:
            # Get the path to external_json directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            external_json_dir = os.path.join(current_dir, "external_json")

            # Load employees
            with open(os.path.join(external_json_dir, "employees.json"), "r") as f:
                employees_data = json.load(f)
                for emp_data in employees_data:
                    employee = EmployeeTable(**emp_data)
                    db.add(employee)

            # Load Jira tickets
            with open(os.path.join(external_json_dir, "jira_tickets.json"), "r") as f:
                tickets_data = json.load(f)
                for ticket_data in tickets_data:
                    ticket = JiraTicketTable(**ticket_data)
                    db.add(ticket)

            # Load deployments
            with open(os.path.join(external_json_dir, "deployments.json"), "r") as f:
                deployments_data = json.load(f)
                for deployment_data in deployments_data:
                    # Convert date string to datetime
                    if isinstance(deployment_data["date"], str):
                        deployment_data["date"] = datetime.fromisoformat(
                            deployment_data["date"].replace("Z", "+00:00")
                        )
                    deployment = DeploymentTable(**deployment_data)
                    db.add(deployment)

            db.commit()
            logger.info("Sample data loaded successfully")

        except Exception as e:
            db.rollback()
            logger.error(f"Error loading sample data: {e}")
            raise

    def get_employees(self) -> List[Employee]:
        """Get all employees from database."""
        db = SessionLocal()
        try:
            employees = db.query(EmployeeTable).all()
            return [Employee.model_validate(emp) for emp in employees]
        finally:
            db.close()

    def get_jira_tickets(self) -> List[JiraTicket]:
        """Get all Jira tickets from database."""
        db = SessionLocal()
        try:
            tickets = db.query(JiraTicketTable).all()
            return [JiraTicket.model_validate(ticket) for ticket in tickets]
        finally:
            db.close()

    def get_deployments(self) -> List[Deployment]:
        """Get all deployments from database."""
        db = SessionLocal()
        try:
            deployments = db.query(DeploymentTable).all()
            return [Deployment.model_validate(deployment) for deployment in deployments]
        finally:
            db.close()

    def get_open_tickets(self) -> List[JiraTicket]:
        """Get all open Jira tickets from database."""
        db = SessionLocal()
        try:
            tickets = db.query(JiraTicketTable).filter(JiraTicketTable.status == "Open").all()
            return [JiraTicket.model_validate(ticket) for ticket in tickets]
        finally:
            db.close()

    def get_recent_deployments(self, count: int = 5) -> List[Deployment]:
        """Get the most recent deployments from database."""
        db = SessionLocal()
        try:
            deployments = db.query(DeploymentTable).order_by(
                DeploymentTable.date.desc()
            ).limit(count).all()
            return [Deployment.model_validate(deployment) for deployment in deployments]
        finally:
            db.close()

    def get_conversation_history(self, limit: int = 100, user_id: str = None) -> List[LogEntry]:
        """Get recent conversation history from database, optionally filtered by user_id."""
        try:
            db = SessionLocal()
            query = db.query(LogEntryTable)
            
            if user_id:
                query = query.filter(LogEntryTable.user_id == user_id)
            
            log_entries = query.order_by(
                LogEntryTable.timestamp.desc()
            ).limit(limit).all()
            
            logs = []
            for entry in log_entries:
                # Parse sources from comma-separated string
                sources = []
                if entry.sources:
                    sources = [s.strip() for s in entry.sources.split(",") if s.strip()]
                
                # Parse feedback from JSON string
                feedback = None
                if entry.feedback:
                    try:
                        import ast
                        feedback = ast.literal_eval(entry.feedback)
                    except:
                        feedback = {"text": entry.feedback}
                
                # Create LogEntry manually to avoid validation issues with sources field
                log_entry = LogEntry(
                    id=entry.id,
                    timestamp=entry.timestamp,
                    query=entry.query,
                    response=entry.response,
                    sources=sources,  # Use parsed list
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

    def add_feedback(self, log_id: int, helpful: bool, feedback_text: str = "") -> bool:
        """Add feedback for a response by updating existing entry."""
        try:
            db = SessionLocal()
            # Find the log entry by id
            log_entry = db.query(LogEntryTable).filter(
                LogEntryTable.id == log_id
            ).first()
            
            if log_entry:
                feedback_data = {
                    "helpful": helpful,
                    "feedback_text": feedback_text,
                    "timestamp": datetime.now().isoformat()
                }
                log_entry.feedback = str(feedback_data)
                db.commit()
                
                # Log feedback to app.log
                from simple_logs import log_action
                feedback_status = "Helpful" if helpful else "Not Helpful"
                log_action(
                    query=f"Feedback on query: {log_entry.query[:50]}...",
                    action=f"User feedback: {feedback_status}",
                    result=f"Feedback: {feedback_text}" if feedback_text else "No additional comment",
                    duration=0.0
                )
                
                db.close()
                return True
            else:
                db.close()
                return False
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return False


# Global instance
data_service = DataService()
