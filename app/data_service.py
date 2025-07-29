"""
Simple data service for Harri AI Assistant.
Loads JSON files and provides basic data access.
"""

import json
import os
from loguru import logger
from typing import List, Optional

from model import Employee, JiraTicket, Deployment


class DataService:
    """Simple service to load and serve JSON data."""

    def __init__(self):
        """Load all JSON data on startup."""
        self.employees: List[Employee] = []
        self.jira_tickets: List[JiraTicket] = []
        self.deployments: List[Deployment] = []
        self._load_data()

    def _load_data(self):
        """Load JSON files into memory."""
        try:
            # Load employees
            with open(os.path.join(config.DATA_DIR, "employees.json"), "r") as f:
                data = json.load(f)
                self.employees = [Employee(**emp) for emp in data]

            # Load Jira tickets
            with open(os.path.join(config.DATA_DIR, "jira_tickets.json"), "r") as f:
                data = json.load(f)
                self.jira_tickets = [JiraTicket(**ticket) for ticket in data]

            # Load deployments
            with open(os.path.join(config.DATA_DIR, "deployments.json"), "r") as f:
                data = json.load(f)
                self.deployments = [Deployment(**deployment) for deployment in data]

            logger.info(
                f" Loaded {len(self.employees)} employees, "
                f"{len(self.jira_tickets)} tickets, "
                f"{len(self.deployments)} deployments"
            )
        except Exception as e:
            logger.error(f"Error loading data: {e}")

    def get_employees(self) -> List[Employee]:
        """Get all employees."""
        return self.employees
        

    def get_open_tickets(self) -> List[JiraTicket]:
        """Get all open Jira tickets."""
        return [ticket for ticket in self.jira_tickets if ticket.status == "Open"]

    def get_recent_deployments(self, count: int = 5) -> List[Deployment]:
        """Get the most recent deployments."""
        return sorted(self.deployments, key=lambda x: x.date, reverse=True)[:count]


# Global instance
data_service = DataService()
