from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .services import get_bot_response
from .models import ChatMessage, DashboardResponse
from .cache import response_cache
from .memory import (
    clear_session_memory,
    clear_all_memories,
    get_memory_stats,
    get_session_count
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage) -> DashboardResponse:
    """
    Chat endpoint that processes user message and generates HTML response.
    Maintains conversation context via session memory.
    
    Uses cache as a FORMAT REFERENCE to ensure consistent UI/UX:
    - If similar query exists: Uses its format as reference, generates NEW content
    - If new query: Generates new format and caches it for future reference
    
    Args:
        message: ChatMessage containing content and optional session_id
    
    Returns:
        DashboardResponse with message, html, and session info
    """
    user_message = message.content
    session_id = message.session_id
    
    logger.info(f"Chat endpoint called - Session: {session_id}, Message: '{user_message}'")
    
    # Get bot response with HTML and conversation memory context
    bot_response, html_content, is_format_consistent = await get_bot_response(user_message, session_id)
    
    response = DashboardResponse(
        message=bot_response,
        html=html_content,
        from_cache=is_format_consistent,
        session_id=session_id
    )

    if is_format_consistent:
        logger.info(f"✅ USING FORMAT REFERENCE - Generated NEW content with consistent format")
    else:
        logger.info(f"🆕 NEW FORMAT - Generated and cached for future consistency")
    
    return response

@app.get("/api/cache-stats")
def get_cache_stats():
    """Get cache statistics and performance metrics."""
    return response_cache.get_stats()

@app.delete("/api/cache")
def clear_cache():
    """Clear all cached responses."""
    response_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.get("/api/sessions/stats")
def get_sessions_stats():
    """Get statistics about active conversation sessions."""
    return {
        "active_sessions": get_session_count(),
        "description": "Number of active conversation sessions with memory"
    }

@app.get("/api/sessions/{session_id}/memory-stats")
def get_session_memory_stats(session_id: str):
    """
    Get statistics about a specific session's conversation memory.
    
    Args:
        session_id: The session identifier
        
    Returns:
        Dict with message count, memory buffer length, and summary
    """
    return get_memory_stats(session_id)

@app.delete("/api/sessions/{session_id}/history")
def clear_session_history(session_id: str):
    """
    Clear conversation history for a specific session.
    
    Args:
        session_id: The session identifier to clear
        
    Returns:
        Confirmation message
    """
    clear_session_memory(session_id)
    logger.info(f"Cleared history for session: {session_id}")
    return {"message": f"Conversation history cleared for session {session_id}"}

@app.delete("/api/sessions/history/all")
def clear_all_session_history():
    """
    Clear conversation history for all sessions.
    
    Returns:
        Confirmation message
    """
    clear_all_memories()
    logger.info("Cleared all session memories")
    return {"message": "All conversation histories cleared"}
