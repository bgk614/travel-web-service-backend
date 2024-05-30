from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    userid: str
    nickname: str
    password: Optional[str] = None
    name: str
    phone: str
    email: EmailStr
    address: str

class UserResponse(BaseModel):
    id: int
    userid: str
    nickname: str
    name: str
    phone: str
    email: str
    address: str

    class Config:
        orm_mode = True