import json
import logging
from langchain_openai import ChatOpenAI
from typing import Optional
from ..config import get_settings
from ..prompts import CONTENT_GENERATION_PROMPT

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()
openai_client = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model_name="gpt-4o")

def analyze_user_intent(user_message: str) -> dict:
    """Use OpenAI to analyze user intent and generate appropriate HTML content"""
    
    logger.info(f"Analyzing user intent for message: {user_message}")
    
    prompt = CONTENT_GENERATION_PROMPT.format(user_message=user_message)

    try:
        response = openai_client.invoke(prompt)
        
        if not response or not response.content:
            logger.error("Empty response from OpenAI API")
            raise ValueError("OpenAI API returned an empty response")
            
        result = response.content
        logger.info(f"Successfully received response from OpenAI (length: {len(result)} chars)")
        logger.debug(f"Response content: {result[:300]}...")
        return result
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
        raise

def get_bot_response(user_message: str) -> tuple[str, Optional[str]]:
    """Get bot response and dynamic HTML content based on user intent"""
    
    logger.info(f"Processing bot response for: '{user_message}'")
    
    try:
        # Analyze user intent and generate content
        response_json = analyze_user_intent(user_message)
        logger.debug(f"Raw response from AI: {response_json[:200]}...")
        
        # Extract JSON from markdown code blocks if present
        clean_response = response_json.strip()
        if clean_response.startswith("```"):
            # Remove markdown code blocks
            clean_response = clean_response.replace("```json", "").replace("```", "").strip()
            logger.debug(f"Extracted JSON from markdown code blocks")
        
        logger.debug(f"Cleaned response: {clean_response[:300]}...")
        response_data = json.loads(clean_response)
        logger.debug(f"Successfully parsed JSON response")
        
        content_type = response_data.get("type", "custom")
        title = response_data.get("title", "Content")
        description = response_data.get("description", "")
        html_content = response_data.get("html", "")
        
        logger.info(f"Content generated - Type: {content_type}, Title: {title}")
        logger.debug(f"HTML content length: {len(html_content)} characters")
        
        if html_content:
            bot_message = f"I've created {content_type} for you: {title}. {description}"
            logger.info(f"Successfully generated content - Bot message: {bot_message}")
            return bot_message, html_content
        else:
            logger.warning("No HTML content generated")
            return "I could not generate the requested content. Please try again with more details.", None
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.debug(f"Failed JSON string: {response_json}")
        return "Sorry, I encountered an error parsing the response. Please try again.", None
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}", exc_info=True)
        return "Sorry, I encountered an error. Please try again.", None


