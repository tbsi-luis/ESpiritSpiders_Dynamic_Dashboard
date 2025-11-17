"""
MCP Service - Handles database queries through Model Context Protocol
Allows OpenAI to intelligently query the PostgreSQL database based on user intent

Note: This implementation uses direct SQLAlchemy queries instead of the deprecated
mcp_servers parameter, while maintaining the MCP concept of intelligent data retrieval.
"""

import logging
import json
from langchain_openai import ChatOpenAI
from sqlalchemy import text, inspect
from typing import Optional, Dict, Any, List
from .config import get_settings
from .database import SessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize standard OpenAI client (without deprecated mcp_servers)
def get_llm_client():
    """
    Get OpenAI client for intent analysis and SQL generation.
    """
    try:
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0.7
        )
        logger.info("✅ OpenAI client initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return None


def query_database_for_content(user_message: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Main MCP-style database query function.
    
    Implements the MCP (Model Context Protocol) concept by:
    1. Using OpenAI to understand user intent
    2. Generating appropriate SQL queries
    3. Executing queries against PostgreSQL
    4. Returning structured data for dashboard generation
    
    Args:
        user_message: User's natural language request
        context: Optional additional context
        
    Returns:
        Dictionary with query results and metadata
    """
    
    logger.info(f"🔍 Querying database for: '{user_message}'")
    
    try:
        # Step 1: Convert user intent to SQL using OpenAI
        logger.info("📝 Analyzing user intent and generating SQL...")
        sql_query = generate_sql_from_intent(user_message)
        
        if not sql_query:
            logger.warning("⚠️ Could not generate SQL from user message")
            return {
                "success": False,
                "error": "Could not understand your request"
            }
        
        # Step 2: Execute the generated SQL query
        logger.info("🗄️ Executing generated SQL query...")
        db_result = execute_sql_query(sql_query)
        
        if not db_result.get("success"):
            logger.warning(f"⚠️ Query execution failed: {db_result.get('error')}")
            return db_result
        
        # Step 3: Format data for use in dashboard
        formatted_data = format_data_for_display(db_result)
        
        logger.info(f"✅ Database query successful: {db_result.get('row_count', 0)} rows")
        
        return {
            "success": True,
            "data": db_result.get("data"),
            "formatted": formatted_data,
            "columns": db_result.get("columns"),
            "row_count": db_result.get("row_count"),
            "query": sql_query
        }
        
    except Exception as e:
        logger.error(f"❌ Database query failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def get_database_schema() -> Dict[str, Any]:
    """
    Get database schema information to help OpenAI understand available tables.
    Uses SQLAlchemy to query database metadata.
    Filters to only relevant tables, excluding system/internal tables.
    
    Returns:
        Dictionary with table names and columns (limited to ~20 tables max)
    """
    
    logger.info("📋 Retrieving database schema...")
    
    # System/internal table patterns to exclude
    exclude_patterns = [
        'pg_', 'sql_', 'information_schema', 'pg_catalog',
        'temp', '_temp', 'cache', 'log', 'session',
        'version', 'metadata', 'audit', 'sys'
    ]
    
    try:
        db = SessionLocal()
        inspector = inspect(db.bind)
        
        all_tables = inspector.get_table_names()
        
        # Filter out system tables and limit to ~20 most relevant tables
        tables = {}
        for table_name in all_tables:
            # Skip if matches excluded patterns
            if any(pattern.lower() in table_name.lower() for pattern in exclude_patterns):
                continue
                
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            tables[table_name] = columns
            
            # Limit to 5 tables for faster testing and minimal tokens
            if len(tables) >= 5:
                break
        
        db.close()
        logger.info(f"✅ Schema retrieved: {len(tables)} tables (filtered from {len(all_tables)})")
        return {
            "success": True,
            "tables": tables
        }
    except Exception as e:
        logger.error(f"❌ Schema retrieval failed: {e}")
        return {
            "success": False,
            "tables": None,
            "error": str(e)
        }


def generate_sql_from_intent(user_message: str) -> Optional[str]:
    """
    Use OpenAI to translate user intent to SQL query.
    
    Args:
        user_message: User's natural language request
        
    Returns:
        SQL query string or None if generation fails
    """
    
    llm = get_llm_client()
    if not llm:
        logger.warning("⚠️ LLM client not available")
        return None
    
    try:
        schema_info = get_database_schema()
        
        if not schema_info.get("success"):
            logger.warning("⚠️ Could not retrieve schema")
            schema_str = "Available tables: users, activity, data"
        else:
            schema_str = "\n".join([
                f"- {table}: {', '.join(cols)}" 
                for table, cols in schema_info.get("tables", {}).items()
            ])
        
        sql_prompt = f"""You are a PostgreSQL expert. Convert the user's request into a valid SELECT query.

DATABASE SCHEMA:
{schema_str}

USER REQUEST: {user_message}

RULES:
1. Generate ONLY a SELECT query
2. No UPDATE, DELETE, or INSERT statements
3. Return ONLY the SQL query, nothing else
4. Use real table and column names from the schema
5. Add WHERE clauses for filtering if needed
6. Use LIMIT to restrict results (max 100 rows)
7. Return valid PostgreSQL syntax

Generate the SQL query:"""

        response = llm.invoke(sql_prompt)
        
        if response and response.content:
            sql_query = response.content.strip()
            
            # Clean up markdown code blocks if present
            if sql_query.startswith("```"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"✅ SQL generated: {sql_query[:80]}...")
            return sql_query
        else:
            logger.warning("⚠️ Empty response from LLM")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to generate SQL: {e}")
        return None


def execute_sql_query(query: str) -> Dict[str, Any]:
    """
    Safely execute a SELECT query on the database.
    
    Args:
        query: SQL query string (SELECT only)
        
    Returns:
        Dictionary with success status, columns, and data
    """
    
    try:
        # Security: Only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            logger.error("❌ Only SELECT queries allowed")
            return {
                "success": False,
                "error": "Only SELECT queries are allowed"
            }
        
        # Execute query
        db = SessionLocal()
        result = db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys() if result.keys() else []
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]
        
        db.close()
        
        logger.info(f"✅ Query executed: {len(data)} rows retrieved")
        
        return {
            "success": True,
            "columns": list(columns),
            "data": data,
            "row_count": len(data)
        }
        
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def format_data_for_display(db_result: Dict[str, Any]) -> str:
    """
    Format database results as human-readable text for LLM processing.
    
    Args:
        db_result: Database query result
        
    Returns:
        Formatted string representation of the data
    """
    
    try:
        data = db_result.get("data", [])
        columns = db_result.get("columns", [])
        
        if not data:
            return "No data found"
        
        # Create simple table format
        lines = []
        lines.append(", ".join(str(c) for c in columns))
        
        for row in data[:10]:  # Limit to first 10 rows for display
            lines.append(", ".join(str(row.get(col, "")) for col in columns))
        
        if len(data) > 10:
            lines.append(f"... and {len(data) - 10} more rows")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"❌ Data formatting failed: {e}")
        return str(db_result.get("data", []))


def validate_mcp_connection() -> bool:
    """
    Test connection to PostgreSQL database.
    
    Returns:
        True if connection is successful, False otherwise
    """
    
    logger.info("🔗 Testing PostgreSQL connection...")
    
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        db.close()
        
        logger.info(f"✅ PostgreSQL connection validated: {str(version)[:50]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False
