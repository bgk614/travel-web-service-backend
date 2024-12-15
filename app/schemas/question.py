from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionBase(BaseModel):
    title: str
    question: str
    asker: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Question(BaseModel):
    title: str
    question: str
    asker: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
