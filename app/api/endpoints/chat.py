from fastapi import APIRouter
from sqlalchemy import select
from app.models.chat import chat
from app.database import database
from app.schemas.chat import ChatMessage

router = APIRouter()

@router.post("/")
async def create_message(item: ChatMessage):
    query = chat.insert().values(sender=item.sender, text=item.text)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

@router.get("/")
async def read_messages():
    query = select(chat)
    results = await database.fetch_all(query)
    return {"messages": results}