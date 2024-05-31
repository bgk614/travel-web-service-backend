from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional

class CheckUserIdRequest(BaseModel):
    userid: str

class CheckNicknameRequest(BaseModel):
    nickname: str

class LoginRequest(BaseModel):
    userid: str
    password: str

class EmailRequest(BaseModel):
    userid: Optional[str] = None
    name: Optional[str] = None
    email: EmailStr
    
    @model_validator(mode='after')
    def check_userid_or_name(cls, values):
        if not values.userid and not values.name:
            raise ValueError('Either userid or name must be provided')
        return values

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    verificationCode: str

class FindIDRequest(BaseModel):
    name: str
    email: EmailStr

class VerifyUserRequest(BaseModel):
    userid: str
    email: EmailStr
    verificationCode: str

class ResetPasswordRequest(BaseModel):
    userid: str
    newPassword: str
