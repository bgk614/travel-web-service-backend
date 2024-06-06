from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Board(BaseModel):
    id: int
    title: str
    contents: str
    created_by: str
    created_at: Optional[datetime] = None
    click_count: int = 0