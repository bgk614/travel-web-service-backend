from fastapi import FastAPI
from app.api.endpoints import board, chat, users, place
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import place as place_model

Base.metadata.create_all(bind=engine)

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
app.include_router(place.router, prefix="/place", tags=["place"])
