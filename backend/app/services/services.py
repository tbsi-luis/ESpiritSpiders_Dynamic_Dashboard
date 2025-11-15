import json
import logging
from langchain_openai import ChatOpenAI
from typing import Optional
from ..config import get_settings
from ..prompts import CONTENT_GENERATION_PROMPT, CONTENT_GENERATION_WITH_FORMAT_REFERENCE
from ..cache import response_cache

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()
openai_client = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model_name="gpt-4o")

def analyze_user_intent(user_message: str, format_reference: Optional[dict] = None) -> dict:
    """
    Use OpenAI to analyze user intent and generate appropriate HTML content.
    If format_reference is provided, uses it as a template for consistent formatting.
    """
    
    logger.info(f"Analyzing user intent for message: {user_message}")
    
    # Choose prompt based on whether we have a format reference
    if format_reference:
        logger.info("🎨 Using format reference to maintain consistent UI/UX")
        prompt = CONTENT_GENERATION_WITH_FORMAT_REFERENCE.format(
            user_message=user_message,
            format_type=format_reference.get('format_type', 'unknown'),
            format_reference=format_reference.get('html_preview', 'N/A')[:500]  # First 500 chars as preview
        )
    else:
        prompt = CONTENT_GENERATION_PROMPT.format(user_message=user_message)

    try:
        response = openai_client.invoke(prompt)
        
        if not response or not response.content:
            logger.error("Empty response from OpenAI API")
            raise ValueError("OpenAI API returned an empty response")
            
        result = response.content
        logger.info(f"Successfully received response from OpenAI (length: {len(result)} chars)")
        return result
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
        raise

def get_bot_response(user_message: str) -> tuple[str, Optional[str], bool]:
    """
    Get bot response and dynamic HTML content based on user intent.
    Uses cache for similar questions to ensure consistent, standardized output format.
    
    If a similar query exists in cache, uses its format as a REFERENCE for the AI to generate
    NEW content with the same layout/structure, ensuring consistent UI/UX.
    
    Returns:
        Tuple of (bot_message, html_content, is_format_consistent)
        - is_format_consistent=True: Used cached format as reference for AI
        - is_format_consistent=False: Generated new format from scratch
    """
    
    logger.info(f"📨 Processing bot response for: '{user_message}'")
    
    # Check cache for similar query - uses format as reference, not as direct output
    cached_entry = response_cache.find_similar(user_message, threshold=0.75)
    format_reference = None
    is_format_consistent = False
    
    if cached_entry:
        logger.info("✅ FOUND SIMILAR QUERY - Using its format as reference for consistency")
        logger.info(f"   Message: {cached_entry['bot_message']}")
        # Extract format info from cached entry for reference
        format_reference = {
            'format_type': response_cache._extract_format_type(cached_entry['html_content']),
            'html_preview': cached_entry['html_content']
        }
        is_format_consistent = True
        response_cache.update_access_count(cached_entry)
    
    try:
        # Analyze user intent and generate content
        if is_format_consistent:
            logger.info("🚀 Generating NEW response using format reference for consistency")
        else:
            logger.info("🚀 Generating NEW response from scratch")
            
        response_json = analyze_user_intent(user_message, format_reference=format_reference)
        
        # Extract JSON from markdown code blocks if present
        clean_response = response_json.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.replace("```json", "").replace("```", "").strip()
        
        response_data = json.loads(clean_response)
        
        content_type = response_data.get("type", "custom")
        title = response_data.get("title", "Content")
        description = response_data.get("description", "")
        html_content = response_data.get("html", "")
        
        logger.info(f"📝 Content generated - Type: {content_type}, Title: {title}")
        
        if html_content:
            bot_message = f"I've created {content_type} for you: {title}. {description}"
            # Cache the successful response for future consistency
            response_cache.add(user_message, bot_message, html_content)
            logger.info("💾 Response cached for future format reference")
            return bot_message, html_content, is_format_consistent
        else:
            logger.warning("No HTML content generated")
            return "I could not generate the requested content. Please try again with more details.", None, False
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return "Sorry, I encountered an error parsing the response. Please try again.", None, False
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}", exc_info=True)
        return "Sorry, I encountered an error. Please try again.", None, False


