from fastapi import FastAPI, HTTPException, Depends
from .models import board, chat, users
from .database import database, get_db
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
import random
import string

# FastAPI 애플리케이션 생성
app = FastAPI()

verification_codes = {}

# CORS 미들웨어 추가
# 모든 출처, 자격 증명, 메소드, 헤더를 허용
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Pydantic 모델 정의
class Board(BaseModel):
    title: str
    contents: str
    created_by: str
    
class ChatMessage(BaseModel):
    sender: str
    text: str

class UserCreate(BaseModel):
    userid: str
    nickname: str
    password: Optional[str] = None  # 비밀번호는 선택사항으로 변경
    name: str
    birthDate: str
    phoneNumber: str
    #email: EmailStr
    #address: str

class UserResponse(BaseModel):
    id: int
    userid: str
    nickname: str
    name: str
    birthDate: str
    phoneNumber: str
    #email: str
    #address: str

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    username: str
    password: str

class PhoneNumberRequest(BaseModel):
    phoneNumber: str

class VerifyCodeRequest(BaseModel):
    phoneNumber: str
    verificationCode: str

class FindIDRequest(BaseModel):
    name: str
    phoneNumber: str

class VerifyUserRequest(BaseModel):
    Id: str
    name: str
    phoneNumber: str
    verificationCode: str

class ResetPasswordRequest(BaseModel):
    Id: str
    newPassword: str

# 애플리케이션 시작 시 데이터베이스 연결
@app.on_event("startup")
async def startup():
    await database.connect()
    print("Database connected!")

# 애플리케이션 종료 시 데이터베이스 연결 해제
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected!")

# 게시글 생성 엔드포인트
@app.post("/board/")
async def create_board(item: Board):
    query = board.insert().values(title=item.title, contents=item.contents, created_by=item.created_by)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

# 모든 게시글 조회 엔드포인트
@app.get("/board/")
async def read_boards():
    query = select(board)
    results = await database.fetch_all(query)
    return {"boards": results}

# 특정 게시글 조회 엔드포인트
@app.get("/board/{board_id}")
async def read_board(board_id: int):
    query = select(board).where(board.c.idx == board_id)  # idx는 테이블의 열 이름으로 가정
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return result

# 특정 게시글 삭제 엔드포인트
@app.delete("/board/{board_id}")
async def delete_board(board_id: int):
    query = board.delete().where(board.c.idx == board_id)  # idx는 테이블의 열 이름으로 가정
    await database.execute(query)
    return {"message": "Board deleted"}

# 채팅 메시지 생성 엔드포인트
@app.post("/chat/")
async def create_message(item: ChatMessage):
    query = chat.insert().values(sender=item.sender, text=item.text)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

# 모든 채팅 메시지 조회 엔드포인트
@app.get("/chat/")
async def read_messages():
    query = select(chat)
    results = await database.fetch_all(query)
    return {"messages": results}

# 유저 정보 조회 엔드포인트
@app.get("/users/", response_model=UserResponse)
async def read_users():
    query = select(users)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

# 유저 정보 업데이트 엔드포인트
@app.put("/users/")
async def update_user(user: UserCreate):
    query = select(users)
    db_user = await database.fetch_one(query)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {
        "userid": user.userid,
        "nickname": user.nickname,
        "name": user.name,
        "phoneNumber": user.phoneNumber,
        #"email": user.email,
        #"address": user.address
    }

    if user.password:  # 비밀번호가 제공된 경우에만 추가
        update_data["password"] = get_password_hash(user.password)  # 실제로는 비밀번호 해싱 필요

    update_query = users.update().values(update_data).where(users.c.id == db_user.id)
    await database.execute(update_query)
    return {**user.dict(exclude_unset=True), "id": db_user.id}

# 사용자 조회 함수
def get_user(db: Session, userid: str):
    query = select(users).where(users.c.userid == userid)
    return db.execute(query).first()

# 사용자 인증 함수
def authenticate_user(db: Session, userid: str, password: str):
    user = get_user(db, userid)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# 회원가입 엔드포인트
@app.post("/signup/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    query = insert(users).values(
        userid=user.userid,
        password=hashed_password,
        nickname=user.nickname,
        name=user.name,
        birthDate=user.birthDate,
        phoneNumber=user.phoneNumber,
        #email=user.email,
        #address=user.address
    )
    try:
        last_record_id = await database.execute(query)
        await database.commit()
        return {**user.dict(), "id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 로그인 엔드포인트
@app.post("/login/")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "user": user}

# 인증번호 요청 엔드포인트
@app.post("/send-code/")
async def send_code(request: PhoneNumberRequest):
    verification_code = ''.join(random.choices(string.digits, k=6))
    verification_codes[request.phoneNumber] = verification_code
    # Here you would send the verification code via SMS
    print(f"Sent code {verification_code} to phone number {request.phoneNumber}")
    return {"message": "Verification code sent"}

# 인증번호 확인 엔드포인트
@app.post("/verify-code/")
async def verify_code(request: VerifyCodeRequest):
    if request.phoneNumber not in verification_codes:
        raise HTTPException(status_code=404, detail="Phone number not found")
    
    if verification_codes[request.phoneNumber] != request.verificationCode:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Remove the verification code once it is verified
    del verification_codes[request.phoneNumber]
    return {"success": True}
    
# 아이디 찾기 엔드포인트
@app.post("/find-id/")
async def find_id(request: FindIDRequest, db: Session = Depends(get_db)):
    query = select(users).where(users.c.name == request.name, users.c.phoneNumber == request.phoneNumber)
    user = await db.execute(query).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"userId": user.userid}

# 인증 엔드포인트
@app.post("/verify-user/")
async def verify_user(request: VerifyUserRequest, db: Session = Depends(get_db)):
    if request.phoneNumber not in verification_codes:
        raise HTTPException(status_code=404, detail="Phone number not found")
    
    if verification_codes[request.phoneNumber] != request.verificationCode:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Verify user details
    user = db.query(users).filter(users.c.userid == request.Id, users.c.name == request.name, users.c.phoneNumber == request.phoneNumber).first()
    if not user:
        raise HTTPException(status_code=400, detail="User details do not match")
    
    # Verification successful, delete the verification code
    del verification_codes[request.phoneNumber]
    return {"success": True}

# 비밀번호 설정 엔드포인트
@app.post("/reset-password/")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(users).filter(users.c.userid == request.Id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = get_password_hash(request.newPassword)
    user.password = hashed_password
    db.commit()
    return {"success": True}