from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .services import get_bot_response
from .models import ChatMessage, DashboardResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
logger.info("FastAPI application initialized")

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
    Chat endpoint that processes user message and generates HTML response
    """
    user_message = message.content
    logger.info(f"Chat endpoint called with message: '{user_message}'")
    
    # Get bot response with HTML
    bot_response, html_content = get_bot_response(user_message)
    
    response = DashboardResponse(
        message=bot_response,
        html=html_content
    )

    logger.info(f"Returning response - Bot message: '{bot_response[:50]}...' - HTML generated: {html_content is not None}")
    return response
