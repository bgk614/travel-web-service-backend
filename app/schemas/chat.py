from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    sender: str
    text: str
    created_at: Optional[datetime] = None
