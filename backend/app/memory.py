"""
Conversation memory management for session-based chat history.
Uses a simple in-memory buffer to maintain context across interactions.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Simple in-memory conversation storage structure
class ConversationBuffer:
    """Simple conversation buffer without external dependency"""
    def __init__(self):
        self.messages = []
        self.summary = ""
    
    def add_message(self, role: str, content: str):
        """Add a message to the buffer"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": str(__import__('datetime').datetime.now())
        })
    
    def get_messages(self, limit: int = 10):
        """Get recent messages up to limit"""
        return self.messages[-limit:] if self.messages else []
    
    def get_buffer_string(self):
        """Get formatted conversation history"""
        if not self.messages:
            return ""
        
        buffer = []
        for msg in self.messages[-10:]:  # Last 10 messages
            role = msg['role'].upper()
            content = msg['content'][:200]  # Limit content length
            buffer.append(f"{role}: {content}")
        
        return "\n".join(buffer)
    
    def clear(self):
        """Clear all messages"""
        self.messages = []
        self.summary = ""

# Global dictionary to store conversation buffers per session
session_memories: Dict[str, ConversationBuffer] = {}

def get_or_create_memory(session_id: str) -> ConversationBuffer:
    """
    Get existing memory for a session or create a new one.
    
    Args:
        session_id: Unique identifier for the conversation session
        
    Returns:
        ConversationBuffer instance for the session
    """
    if session_id not in session_memories:
        logger.info(f"Creating new memory for session: {session_id}")
        session_memories[session_id] = ConversationBuffer()
    
    return session_memories[session_id]

def add_user_message(session_id: str, message: str) -> None:
    """
    Add a user message to the conversation memory.
    
    Args:
        session_id: Unique identifier for the conversation session
        message: User's message content
    """
    memory = get_or_create_memory(session_id)
    memory.add_message("user", message)
    logger.debug(f"Added user message to session {session_id}")

def add_ai_message(session_id: str, message: str) -> None:
    """
    Add an AI message to the conversation memory.
    
    Args:
        session_id: Unique identifier for the conversation session
        message: AI/Bot's message content
    """
    memory = get_or_create_memory(session_id)
    memory.add_message("assistant", message)
    logger.debug(f"Added AI message to session {session_id}")

def get_memory_variables(session_id: str) -> str:
    """
    Get the formatted memory buffer for a session.
    This includes the conversation history/summary.
    
    Args:
        session_id: Unique identifier for the conversation session
        
    Returns:
        String containing conversation history/summary
    """
    memory = get_or_create_memory(session_id)
    return memory.get_buffer_string()

def get_chat_history(session_id: str) -> list:
    """
    Get the full chat history for a session in message format.
    
    Args:
        session_id: Unique identifier for the conversation session
        
    Returns:
        List of message dicts with 'role' and 'content' keys
    """
    memory = get_or_create_memory(session_id)
    messages = []
    
    for msg in memory.get_messages():
        messages.append({
            "role": msg['role'],
            "content": msg['content']
        })
    
    return messages

def clear_session_memory(session_id: str) -> None:
    """
    Clear conversation memory for a specific session.
    
    Args:
        session_id: Unique identifier for the conversation session
    """
    if session_id in session_memories:
        del session_memories[session_id]
        logger.info(f"Cleared memory for session: {session_id}")

def clear_all_memories() -> None:
    """Clear all conversation memories from all sessions."""
    session_memories.clear()
    logger.info("Cleared all session memories")

def get_session_count() -> int:
    """Get the number of active sessions with memories."""
    return len(session_memories)

def get_memory_stats(session_id: str) -> dict:
    """
    Get statistics about a session's memory usage.
    
    Args:
        session_id: Unique identifier for the conversation session
        
    Returns:
        Dict with memory statistics
    """
    memory = get_or_create_memory(session_id)
    history = get_chat_history(session_id)
    buffer = memory.get_buffer_string()
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "buffer_length": len(buffer),
        "summary": buffer[:200] + "..." if len(buffer) > 200 else buffer
    }
