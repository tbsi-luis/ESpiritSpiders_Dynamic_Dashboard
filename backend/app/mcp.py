from langchain_openai import ChatOpenAI
from urllib.parse import quote_plus
import os

password = quote_plus("admin@Adm!n")
database_url = f"postgresql://people_navee:{password}@192.168.2.131:5432/Espider_10282025"

mcp_config = {
    "postgres": {
        "command": "mcp-server-postgres",
        "args": ["--connection-string", database_url],
        "transport": "stdio"
    }
}

llm = ChatOpenAI(
    model="gpt-4.1",
    mcp_servers=mcp_config
)

resp = llm.invoke("Show 5 active users from the database.")
print(resp)