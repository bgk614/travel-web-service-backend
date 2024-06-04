from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update, delete
from app.models.question import question
from app.database import database
from app.schemas.question import QuestionCreate, QuestionResponse, Question

router = APIRouter()

@router.post("/", response_model=QuestionResponse)
async def create_question(item: QuestionCreate):
    query = question.insert().values(title=item.title, question=item.question, asker=item.asker)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

@router.get("/")
async def read_questions():
    query = select(question)
    results = await database.fetch_all(query)
    return {"questions": results}

@router.get("/{question_id}", response_model=QuestionResponse)
async def read_question(question_id: int):
    query = select(question).where(question.c.id == question_id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="question not found")
    return result

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, item: QuestionCreate):
    query = update(question).where(question.c.id == question_id).values(
        title=item.title, question=item.question, asker=item.asker, updated_at=text('CURRENT_TIMESTAMP'))
    await database.execute(query)
    return {**item.dict(), "id": question_id}

@router.delete("/{question_id}")
async def delete_question(question_id: int):
    query = delete(question).where(question.c.id == question_id)
    await database.execute(query)
    return {"message": "question deleted"}
