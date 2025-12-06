"""
Optimized database handler for real data retrieval via MCP.
Ensures all data queries return ONLY real database values, never generated/sample data.
"""

import json
import logging
from typing import Dict, Optional, Any, List
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DatabaseHandler:
    """
    Specialized handler for database queries via MCP.
    Ensures all queries return ONLY real data from PostgreSQL.
    """
    
    def __init__(self):
        self.agent = None
        self.client = None
    
    async def initialize_mcp(self):
        """Initialize MCP client for database access"""
        if self.client is not None:
            return self.client
        
        try:
            NODE_PATH = "C:\\nvm4w\\nodejs\\node.exe"
            SERVER_JS = "C:\\Users\\bandivas_l\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-postgres\\dist\\index.js"
            
            self.client = MultiServerMCPClient({
                "postgres": {
                    "command": NODE_PATH,
                    "transport": "stdio",
                    "args": [SERVER_JS, settings.DATABASE_URL],
                }
            })
            
            logger.info("✅ MCP client initialized successfully")
            return self.client
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP client: {e}")
            raise
    
    async def initialize_agent(self):
        """Initialize the ReAct agent for database queries"""
        if self.agent is not None:
            return self.agent
        
        try:
            await self.initialize_mcp()
            tools = await self.client.get_tools()
            
            llm = ChatOpenAI(model="gpt-5", temperature=0)
            self.agent = create_react_agent(model=llm, tools=tools)
            
            logger.info("✅ Database agent initialized successfully")
            return self.agent
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise
    
    async def query_database(self, user_message: str) -> Optional[str]:
        """
        Query database for real data based on user message.
        
        Args:
            user_message: User's request that may contain data query intent
            
        Returns:
            Raw database query results or None if no query needed
        """
        try:
            # Initialize agent if needed
            if self.agent is None:
                await self.initialize_agent()
            
            logger.info(f"🔍 Querying database for: {user_message}")
            
            # Build a system prompt that enforces real data retrieval
            system_prompt = """You are a PostgreSQL database expert. Your task is to:
1. Analyze the user's request
2. Write SQL queries to fetch REAL data from the database
3. Execute the queries and return the ACTUAL results
4. NEVER generate, create, or assume data
5. If a query returns no results, explicitly state that the table/query has no data
6. Return the EXACT data from the database, nothing else

Important: Only return actual database results. If the query finds nothing, say so explicitly."""
            
            result = await self.agent.ainvoke({
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            })
            
            if "messages" in result and len(result["messages"]) > 0:
                database_result = result["messages"][-1].content
                logger.info(f"✅ Database query returned {len(str(database_result))} chars of data")
                return database_result
            else:
                logger.warning("⚠️ Database query returned no results")
                return None
                
        except Exception as e:
            logger.error(f"❌ Database query error: {e}")
            return None
    
    def should_query_database(self, user_message: str) -> bool:
        """
        Determine if user message requires database query.
        
        Args:
            user_message: User's message
            
        Returns:
            True if database query is needed
        """
        data_keywords = [
            "show", "get", "retrieve", "fetch", "list", "display", "find", 
            "query", "search", "active", "data", "database", "user", "table", 
            "select", "count", "report", "summary", "statistics", "stats",
            "information", "details", "records", "entries", "rows", "results",
            "what", "how many", "how much", "total", "list of", "all",
            "recent", "latest", "historical", "trend", "analysis"
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in data_keywords)
    
    async def get_database_context(self, user_message: str) -> Optional[str]:
        """
        Get real database context if user message requires data retrieval.
        
        Args:
            user_message: User's message
            
        Returns:
            Formatted database context string or None
        """
        if not self.should_query_database(user_message):
            logger.info("📌 Message does not require database query")
            return None
        
        logger.info("📊 Message requires database query - fetching real data")
        database_result = await self.query_database(user_message)
        
        if database_result:
            # Validate that result contains actual data (not generated)
            return f"\n\n📊 REAL DATABASE DATA AVAILABLE:\n{str(database_result)[:3000]}"
        else:
            # Database query returned no data - inform the user
            return "\n\n📊 DATABASE QUERY RESULT: No data found in database for this request. Please verify your query or try a different search criteria."


# Global database handler instance
_db_handler: Optional[DatabaseHandler] = None

async def get_database_handler() -> DatabaseHandler:
    """Get or create global database handler instance"""
    global _db_handler
    if _db_handler is None:
        _db_handler = DatabaseHandler()
    return _db_handler

async def get_real_database_context(user_message: str) -> Optional[str]:
    """
    Public function to get real database context for a user message.
    
    Args:
        user_message: User's message
        
    Returns:
        Database context string with real data, or None
    """
    handler = await get_database_handler()
    return await handler.get_database_context(user_message)
