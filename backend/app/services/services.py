import json
import logging
from langchain_openai import ChatOpenAI
from typing import Optional, Tuple, List
from ..config import get_settings
from ..prompts import CONTENT_GENERATION_PROMPT, CONTENT_GENERATION_WITH_FORMAT_REFERENCE
from ..cache import response_cache
from ..memory import (
    get_or_create_memory,
    add_user_message,
    add_ai_message,
    get_chat_history
)
from ..database_handler import get_real_database_context
import asyncio
import sys
import os

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()
openai_client = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model_name="gpt-5")

# MCP connection validation function
def validate_mcp_connection():
    """Validate that MCP connection is available."""
    try:
        connection_status = True  # Implement actual validation if needed
        return connection_status
    except Exception as e:
        logger.error(f"Error validating MCP connection: {e}")
        return False

async def analyze_user_intent(
    user_message: str,
    session_id: str,
    format_reference: Optional[dict] = None
) -> dict:
    """
    Use OpenAI to analyze user intent and generate appropriate HTML content.
    Integrates with MCP to fetch REAL database data when needed.
    Now maintains conversation context via session memory.
    IMPORTANT: This function uses ONLY real database data - never generates sample data.
    """

    logger.info(f"Analyzing user intent for session {session_id}: {user_message}")

    # Get real database context if user message requires data retrieval
    db_context_str = await get_real_database_context(user_message)
    if db_context_str:
        logger.info(f"✅ Real database context retrieved ({len(db_context_str)} chars)")
    else:
        logger.info("📌 No database context needed or no data available")

    # Get conversation history from memory
    chat_history = get_chat_history(session_id)
    memory_context = ""
    
    if chat_history:
        logger.info(f"  📚 Including {len(chat_history)} previous messages from memory")
        memory_context = "\n\n📚 CONVERSATION HISTORY:\n"
        for msg in chat_history[-10:]:  # Include last 10 messages to stay within token limits
            role = msg['role'].upper()
            memory_context += f"{role}: {msg['content']}\n"

    # Build the final prompt with or without format reference
    if format_reference:
        logger.info("  Using format reference to maintain consistent UI/UX")
        prompt = CONTENT_GENERATION_WITH_FORMAT_REFERENCE.format(
            user_message=user_message,
            format_type=format_reference.get('format_type', 'unknown'),
            format_reference=format_reference.get('html_preview', 'N/A')[:500]
        ) + memory_context + (db_context_str if db_context_str else "")
    else:
        prompt = CONTENT_GENERATION_PROMPT.replace("{user_message}", user_message) + memory_context + (db_context_str if db_context_str else "")
    try:
        # Fetch response from OpenAI using the constructed prompt
        response = openai_client.invoke(prompt)

        if not response or not response.content:
            logger.error("Empty response from OpenAI API")
            raise ValueError("OpenAI API returned an empty response")

        result = response.content
        logger.info(f"Successfully received response from OpenAI (length: {len(result)} chars)")
        logger.info(f"  📊 Data source: {'Real Database' if db_context_str else 'No database query'}")
        return result
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
        raise


async def get_bot_response(user_message: str, session_id: str) -> Tuple[str, str, bool]:
    """
    Main endpoint function that processes user messages and returns bot response with HTML.
    Now maintains conversation context via session memory.
    
    Args:
        user_message: The user's message input
        session_id: Unique session identifier for conversation tracking
    
    Returns:
        Tuple of (bot_message, html_content, is_format_consistent)
    """
    try:
        # Add user message to session memory
        add_user_message(session_id, user_message)
        
        # Check cache for similar queries
        cached_entry = response_cache.find_similar(user_message)
        is_format_consistent = cached_entry is not None
        
        if cached_entry:
            logger.info(f"📦 Cache HIT: Found similar cached response")
            response_cache.update_access_count(cached_entry)
            text_content = cached_entry['bot_message']
            html_content = cached_entry['html_content']
            
            # Add bot response to memory even if from cache
            add_ai_message(session_id, text_content)
            
            return text_content, html_content, is_format_consistent
        
        format_reference = None
        
        # Get the response (with or without format reference)
        bot_response = await analyze_user_intent(user_message, session_id, format_reference)
        
        # Extract HTML if present, or generate default
        try:
            response_data = json.loads(bot_response) if isinstance(bot_response, str) else bot_response
            html_content = response_data.get('html', '<p>Response received</p>')
            text_content = response_data.get('text', 'Response processed')
        except (json.JSONDecodeError, AttributeError):
            # If response is plain text, use it as is
            html_content = f'<p>{bot_response}</p>'
            text_content = bot_response
        
        # Add bot response to session memory
        add_ai_message(session_id, text_content)
        
        # Cache the response for future use
        response_cache.add(user_message, text_content, html_content)
        
        return text_content, html_content, is_format_consistent
        
    except Exception as e:
        logger.error(f"Error in get_bot_response: {str(e)}", exc_info=True)
        error_html = f'<p style="color: red;">Error processing request: {str(e)}</p>'
        error_message = f"Error: {str(e)}"
        
        # Add error to memory for context
        add_ai_message(session_id, error_message)
        
        return error_message, error_html, False
