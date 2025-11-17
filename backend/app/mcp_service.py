"""
MCP Service - Handles database queries through Model Context Protocol
Allows OpenAI to intelligently query the PostgreSQL database based on user intent
"""

import logging
from langchain_openai import ChatOpenAI
from urllib.parse import quote_plus
from typing import Optional, Dict, Any
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize MCP-enabled LLM
def get_mcp_client():
    """
    Get or create an OpenAI client configured with MCP for PostgreSQL access.
    
    This allows the LLM to:
    1. Understand user intent
    2. Generate appropriate SQL queries
    3. Access real data from the database
    4. Process and return results
    """
    
    # Construct database URL with encoded password
    password = quote_plus(settings.DATABASE_PASSWORD)
    database_url = f"postgresql://{settings.DATABASE_USER}:{password}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
    
    mcp_config = {
        "postgres": {
            "command": "mcp-server-postgres",
            "args": ["--connection-string", database_url],
            "transport": "stdio"
        }
    }
    
    try:
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o",
            mcp_servers=mcp_config
        )
        logger.info("✅ MCP-enabled OpenAI client initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP client: {e}")
        raise


def query_database_for_content(user_message: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Use MCP to intelligently query the database based on user message.
    
    The LLM will:
    1. Parse the user's request
    2. Generate appropriate SQL queries
    3. Execute queries via MCP
    4. Return structured data
    
    Args:
        user_message: User's natural language request
        context: Optional additional context for the query
        
    Returns:
        Dictionary with query results and metadata
    """
    
    logger.info(f"🔍 Querying database via MCP for: '{user_message}'")
    
    # Build the prompt that instructs OpenAI to use MCP for database access
    mcp_prompt = f"""You are a database assistant with access to a PostgreSQL database via MCP.

User Request: {user_message}

{f"Additional Context: {context}" if context else ""}

Your task:
1. Understand what data the user is asking for
2. Use your PostgreSQL MCP tool to query the database
3. Retrieve relevant data
4. Return the data in a structured JSON format

Guidelines:
- Use actual database queries to get real data (not mock data)
- If asking about users, query the 'people' table (or similar)
- If asking about activity, query relevant activity tables
- Include relevant fields and filters
- Return at least 5-10 rows of data when possible
- Structure the response as JSON with clear field names
- Include metadata about the query (table, count, etc.)

Please query the database and return the results."""

    try:
        mcp_client = get_mcp_client()
        
        logger.info("📊 Executing MCP database query...")
        response = mcp_client.invoke(mcp_prompt)
        
        if response and response.content:
            logger.info(f"✅ MCP query successful - Retrieved data")
            return {
                "success": True,
                "data": response.content,
                "source": "mcp_database",
                "query_intent": user_message
            }
        else:
            logger.warning("⚠️ MCP returned empty response")
            return {
                "success": False,
                "data": None,
                "error": "MCP returned empty response",
                "source": "mcp_database"
            }
            
    except Exception as e:
        logger.error(f"❌ MCP query failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "source": "mcp_database"
        }


def get_database_schema() -> Dict[str, Any]:
    """
    Get database schema information to help OpenAI understand available tables.
    Uses MCP to query database metadata.
    
    Returns:
        Dictionary with table names, columns, and structure
    """
    
    logger.info("📋 Retrieving database schema via MCP...")
    
    schema_prompt = """You are a database analyst. Using your PostgreSQL MCP access, provide a summary of the database schema.

Please:
1. List all available tables
2. For each table, list the column names and their data types
3. Include any notable relationships or constraints
4. Return as structured JSON

Focus on the main data tables (exclude system tables)."""

    try:
        mcp_client = get_mcp_client()
        response = mcp_client.invoke(schema_prompt)
        
        if response and response.content:
            logger.info("✅ Schema retrieved successfully")
            return {
                "success": True,
                "schema": response.content
            }
        else:
            logger.warning("⚠️ Failed to retrieve schema")
            return {
                "success": False,
                "schema": None
            }
            
    except Exception as e:
        logger.error(f"❌ Schema retrieval failed: {str(e)}")
        return {
            "success": False,
            "schema": None,
            "error": str(e)
        }


def validate_mcp_connection() -> bool:
    """
    Test MCP connection to PostgreSQL database.
    
    Returns:
        True if connection is successful, False otherwise
    """
    
    logger.info("🔗 Testing MCP PostgreSQL connection...")
    
    test_prompt = "Show me the PostgreSQL server version and current database connection info."
    
    try:
        mcp_client = get_mcp_client()
        response = mcp_client.invoke(test_prompt)
        
        if response and response.content:
            logger.info("✅ MCP connection validated successfully")
            logger.info(f"   Server info: {response.content[:100]}...")
            return True
        else:
            logger.warning("⚠️ MCP connection test returned empty response")
            return False
            
    except Exception as e:
        logger.error(f"❌ MCP connection test failed: {str(e)}")
        return False
