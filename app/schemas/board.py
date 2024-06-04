from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Board(BaseModel):
    title: str
    contents: str
    created_by: str
    created_at: Optional[datetime] = None