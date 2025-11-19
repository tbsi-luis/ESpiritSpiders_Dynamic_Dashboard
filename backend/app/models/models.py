from pydantic import BaseModel
from typing import Optional
import uuid

class ChatMessage(BaseModel):
    content: str
    session_id: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())

class DashboardResponse(BaseModel):
    message: str
    html: Optional[str] = None
    from_cache: bool = False
    session_id: Optional[str] = None

