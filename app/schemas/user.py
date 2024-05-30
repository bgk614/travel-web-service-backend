from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    userid: str
    password: str
    nickname: str
    name: str
    birthdate: date
    phone: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    userid: str
    nickname: str
    name: str
    birthdate: date
    phone: str
    email: EmailStr

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    userid: str
    password: str

class PhoneRequest(BaseModel):
    phone: str

class VerifyCodeRequest(BaseModel):
    phone: str
    verificationcode: str

class FindIDRequest(BaseModel):
    name: str
    phone: str

class VerifyUserRequest(BaseModel):
    id: str
    name: str
    phone: str
    verificationcode: str

class ResetPasswordRequest(BaseModel):
    id: str
    newpassword: str

class UserUpdate(BaseModel):
    id: Optional[int]
    userid: str
    password: Optional[str]
    nickname: str
    name: str
    birthdate: date
    phone: str
    email: EmailStr
