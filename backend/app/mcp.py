from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent 
from app.config import get_settings
import asyncio
import logging

settings = get_settings()

logging.basicConfig(level=logging.DEBUG)

async def make_graph():
    NODE_PATH = "C:\\nvm4w\\nodejs\\node.exe"
    SERVER_JS = "C:\\Users\\bandivas_l\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-postgres\\dist\\index.js"

    client = MultiServerMCPClient({
        "postgres": {
            "command": NODE_PATH,
            "transport": "stdio",
            "args": [SERVER_JS, settings.DATABASE_URL],
        }
    })

    tools = await client.get_tools()

    llm = ChatOpenAI(model="gpt-4", temperature=0)

    # FIX 1: Remove 'state_modifier' and 'messages_modifier'. 
    # Just pass the model and tools.
    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    return agent

async def main():
    agent = await make_graph()

    print("Agent created, running query...")

    # Define your system prompt here
    system_instruction = (
        "You are a PostgreSQL expert assistant. "
        "Use PostgreSQL syntax only. "
        "To list tables, use information_schema.tables. "
        "**CRITICAL RULE:** If a query fails because a table (relation) does not exist, "
        "your next step MUST be to search the `information_schema.tables` using the LIKE operator "
        "with a wildcard (%) to find similar or correctly spelled table names, "
        "and then inform the user of the potential corrections."
    )
    
    # FIX 2: Pass the system prompt as the FIRST message in the list
    result = await agent.ainvoke({
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": "List 5 full name from the table reliever_request_line PostgreSQL database."}
        ]
    })

    print("RESULT:")
    if "messages" in result:
        print(result["messages"][-1].content)
    else:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())