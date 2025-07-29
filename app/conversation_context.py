#!/usr/bin/env python3
"""
Conversation Context Service - Uses existing log entries as conversation memory.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from model import LogEntryTable

logger = logging.getLogger(__name__)

def get_conversation_context(user_id: str, max_context_length: int = 2000) -> str:
    """
    Get conversation context from existing log entries for a user.
    
    Args:
        user_id: User identifier
        max_context_length: Maximum length of context to return
        
    Returns:
        Context string for the LLM
    """
    try:
        db = SessionLocal()
        
        # Get recent conversation history for this user (last 5 interactions)
        recent_logs = db.query(LogEntryTable).filter(
            LogEntryTable.user_id == user_id
        ).order_by(
            LogEntryTable.timestamp.desc()
        ).limit(5).all()
        
        if not recent_logs:
            return ""
        
        # Build context from recent conversation (reverse to get chronological order)
        context_parts = []
        total_length = 0
        
        for log in reversed(recent_logs):
            
            # Parse sources if available
            sources = []
            if log.sources:
                try:
                    sources = [s.strip() for s in log.sources.split(',') if s.strip()]
                except:
                    sources = []
            
            # Create conversation turn context
            turn_context = f"User: {log.query}\nAssistant: {log.response}"
            
            # Add sources if available
            if sources:
                turn_context += f"\nSources used: {', '.join(sources)}"
            
            if total_length + len(turn_context) > max_context_length:
                break
            
            context_parts.append(turn_context)
            total_length += len(turn_context)
        
        db.close()
        
        if context_parts:
            return "\n\n".join(context_parts)
        else:
            return ""
            
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        if 'db' in locals():
            db.close()
        return ""



def get_conversation_stats(user_id: str) -> Dict[str, Any]:
    """
    Get conversation statistics for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with conversation statistics
    """
    try:
        db = SessionLocal()
        
        # Total conversations
        total_conversations = db.query(LogEntryTable).filter(
            LogEntryTable.user_id == user_id
        ).count()
        
        # Recent conversations (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_conversations = db.query(LogEntryTable).filter(
            LogEntryTable.user_id == user_id,
            LogEntryTable.timestamp >= yesterday
        ).count()
        
        # Query type distribution
        query_types = db.query(
            LogEntryTable.query_type,
            func.count(LogEntryTable.id)
        ).filter(
            LogEntryTable.user_id == user_id
        ).group_by(
            LogEntryTable.query_type
        ).all()
        
        # Convert query_types to a dictionary
        # we need to convert the query_types to a dictionary
        # so that we can use it in the UI
        # query_types is a list of tuples
        # it maps each query_type to the number of times it has occurred
        query_type_distribution = {qt[0]: qt[1] for qt in query_types}
        
        db.close()
        
        return {
            "total_conversations": total_conversations,
            "recent_conversations_24h": recent_conversations,
            "query_type_distribution": query_type_distribution
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation stats: {e}")
        if 'db' in locals():
            db.close()
        return {} 