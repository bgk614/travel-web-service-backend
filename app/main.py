from fastapi import FastAPI
from app.api.endpoints import board, chat, users, notice, question, answer
from app.database import database
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(board.router, prefix="/board", tags=["board"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(notice.router, prefix="/notice", tags=["notice"])
app.include_router(question.router, prefix="/question", tags=["question"])
app.include_router(answer.router, prefix="/answer", tags=["answer"])

@app.on_event("startup")
async def startup():
    await database.connect()
    print("Database connected!")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected!")