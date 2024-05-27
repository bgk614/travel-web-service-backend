from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnswerCreate(BaseModel):
    question_id: int
    answer: str
    responder: Optional[str] = "Anonymous"

class Answer(AnswerCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Answer(BaseModel):
    answer: str
    responder: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
