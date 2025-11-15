from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    content: str

class DashboardResponse(BaseModel):
    message: str
    html: Optional[str] = None
