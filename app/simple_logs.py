#!/usr/bin/env python3
"""
Simple logging for Harri AI Assistant using existing database structure.
"""

import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from model import LogEntryTable

def log_action(query, action, result=None, error=None, duration=None):
    """Log a simple action using existing database structure."""
    try:
        # Log to existing database
        db = SessionLocal()
        
        # Create log entry
        log_entry = LogEntryTable(
            timestamp=datetime.utcnow(),
            query=query,
            response=action,
            sources=json.dumps([action]) if action else "[]",
            query_type="log",
            processing_time=duration or 0.0,
            user_id=None,
            feedback=json.dumps({"result": result, "error": error}) if result or error else None
        )
        
        db.add(log_entry)
        db.commit()
        db.close()
        
        # Also log to file for quick viewing
        with open("app.log", "a") as f:
            timestamp = datetime.now().isoformat()
            duration_str = f"{duration:.3f}s" if duration is not None else "N/A"
            log_line = f"{timestamp} | {action} | {query[:50]}... | {duration_str}"
            if error:
                log_line += f" | ERROR: {error}"
            f.write(log_line + "\n")
            
    except Exception as e:
        print(f"Failed to log: {e}")

def get_logs(limit=50):
    """Get recent logs from existing database."""
    try:
        db = SessionLocal()
        
        logs = db.query(LogEntryTable).order_by(
            LogEntryTable.timestamp.desc()
        ).limit(limit).all()
        
        result = []
        for log in logs:
            # Ensure timestamp is serializable
            timestamp = log.timestamp
            if hasattr(timestamp, 'isoformat'):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = str(timestamp)
            
            # Ensure all values are JSON-serializable
            result.append({
                "timestamp": timestamp_str,
                "query": str(log.query) if log.query else "",
                "action": str(log.response) if log.response else "",
                "result": str(log.feedback) if log.feedback else None,
                "error": None,  # Could parse from feedback if needed
                "duration": float(log.processing_time) if log.processing_time is not None else 0.0
            })
        
        db.close()
        return result
        
    except Exception as e:
        print(f"Failed to get logs: {e}")
        return []

def print_logs(limit=20):
    """Print logs in a simple format."""
    logs = get_logs(limit)
    
    print(f"\n=== Recent Logs (Last {len(logs)}) ===")
    for log in logs:
        timestamp = log['timestamp'][:19]
        action = log['action']
        query = log['query'][:50] + "..." if len(log['query']) > 50 else log['query']
        duration = log['duration']
        result = log['result']
        
        print(f"[{timestamp}] {action}")
        print(f"  Query: {query}")
        if duration:
            print(f"  Duration: {duration:.3f}s")
        if result:
            print(f"  Result: {result}")
        print()

def view_logs():
    """Simple function to view logs."""
    print_logs(20) 