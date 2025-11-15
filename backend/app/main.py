from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .services import get_bot_response
from .models import ChatMessage, DashboardResponse
from .cache import response_cache

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
    
    Uses cache as a FORMAT REFERENCE to ensure consistent UI/UX:
    - If similar query exists: Uses its format as reference, generates NEW content
    - If new query: Generates new format and caches it for future reference
    """
    user_message = message.content
    logger.info(f"Chat endpoint called with message: '{user_message}'")
    
    # Get bot response with HTML
    bot_response, html_content, is_format_consistent = get_bot_response(user_message)
    
    response = DashboardResponse(
        message=bot_response,
        html=html_content,
        from_cache=is_format_consistent
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
