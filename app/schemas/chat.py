from pydantic import BaseModel

class ChatMessage(BaseModel):
    sender: str
    text: str