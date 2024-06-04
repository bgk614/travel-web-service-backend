from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoticeCreate(BaseModel):
    title: str
    content: str

class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
