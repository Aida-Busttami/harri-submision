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
from model import Employee, JiraTicket, Deployment, EmployeeTable, JiraTicketTable, DeploymentTable


class DataService:
    """Simple service to load and serve data from database."""

    def __init__(self):
        """Initialize database with sample data if empty."""
        self._init_database()

    def _init_database(self):
        """Initialize database with sample data from JSON files if tables are empty."""
        db = SessionLocal()
        try:
            # Check if data already exists
            employee_count = db.query(EmployeeTable).count()
            if employee_count == 0:
                logger.info("Initializing database with sample data...")
                self._load_sample_data(db)
                logger.info("Database initialized successfully")
            else:
                logger.info(f"Database already contains {employee_count} employees")
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


# Global instance
data_service = DataService()
