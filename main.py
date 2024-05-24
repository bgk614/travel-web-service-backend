from fastapi import FastAPI, HTTPException, Depends
from .models import board, chat, users
from .database import database
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import select
from typing import List, Optional

# FastAPI 애플리케이션 생성
app = FastAPI()

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
        "phone": user.phone,
        "email": user.email,
        "address": user.address
    }

    if user.password:  # 비밀번호가 제공된 경우에만 추가
        update_data["password"] = user.password  # 실제로는 비밀번호 해싱 필요

    update_query = users.update().values(update_data).where(users.c.id == db_user.id)
    await database.execute(update_query)
    return {**user.dict(exclude_unset=True), "id": db_user.id}