from openai import OpenAI
import os
import json
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.models.chat import chat
from app.database import database
from app.schemas.chat import ChatMessage
from datetime import datetime

router = APIRouter()

with open('secrets.json', 'r') as file:
    config = json.load(file)
    OpenAI.api_key = config['OPENAI_API_KEY']
    
client = OpenAI(api_key=OpenAI.api_key)

@router.post("/", response_model=ChatMessage)
async def create_message(item: ChatMessage):
    query = chat.insert().values(sender=item.sender, text=item.text)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id, "created_at": datetime.now()}

@router.get("/", response_model=dict)
async def read_messages():
    query = select(chat.c.id, chat.c.sender, chat.c.text, chat.c.created_at)
    results = await database.fetch_all(query)
    messages = [ChatMessage(**dict(result)) for result in results]
    return {"messages": messages}

@router.post("/query_chatgpt/", response_model=ChatMessage)
async def query_chatgpt(item: ChatMessage):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": item.text}
            ]
        )
        response_text = response.choices[0].message.content

        # 응답을 데이터베이스에 저장
        query = chat.insert().values(sender="chatgpt", text=response_text)
        last_record_id = await database.execute(query)

        return {"sender": "chatgpt", "text": response_text, "created_at": datetime.now(), "id": last_record_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))