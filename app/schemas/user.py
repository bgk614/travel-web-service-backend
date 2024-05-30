from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    id: int  
    userid: str
    nickname: str
    password: Optional[str] = None
    name: str
    phone: str
    email: EmailStr
    birthdate: date  

class UserResponse(BaseModel):
    id: int
    userid: str
    nickname: str
    name: str
    phone: str
    email: str
    birthdate: date  

    class Config:
        orm_mode = True
