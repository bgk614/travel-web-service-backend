from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update, delete, insert
from app.models.answer import answer
from app.database import database
from app.schemas.answer import AnswerCreate, Answer
from datetime import datetime
from typing import List, Optional
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=Answer)
async def create_or_update_answer(answer_create: AnswerCreate):
    try:
        # Check if the answer already exists
        query = select(answer.c.id, answer.c.answer, answer.c.responder, answer.c.created_at, answer.c.updated_at).where(answer.c.question_id == answer_create.question_id)
        existing_answer = await database.fetch_one(query)

        if existing_answer:
            # Update the existing answer
            query = (
                update(answer)
                .where(answer.c.id == existing_answer.id)
                .values(
                    answer=answer_create.answer, 
                    responder=answer_create.responder or existing_answer.responder,
                    updated_at=datetime.utcnow()
                )
            )
            await database.execute(query)
            return {**existing_answer, **answer_create.dict(), "updated_at": datetime.utcnow()}

        # Insert a new answer if none exists
        query = insert(answer).values(
            question_id=answer_create.question_id, 
            answer=answer_create.answer, 
            responder=answer_create.responder or "Anonymous",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        last_record_id = await database.execute(query)
        return {
            **answer_create.dict(), 
            "id": last_record_id, 
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error creating or updating answer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[Answer])
async def read_answers():
    try:
        query = select(answer)
        return await database.fetch_all(query)
    except Exception as e:
        logger.error(f"Error reading answers: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/question/{question_id}", response_model=Answer)
async def get_answer_by_question_id(question_id: int):
    try:
        query = select(answer).where(answer.c.question_id == question_id)
        result = await database.fetch_one(query)
        if not result:
            raise HTTPException(status_code=404, detail="Answer not found")
        return result
    except Exception as e:
        logger.error(f"Error fetching answer by question_id {question_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{answer_id}", response_model=Answer)
async def read_answer(answer_id: int):
    try:
        query = select(answer).where(answer.c.id == answer_id)
        answer_record = await database.fetch_one(query)
        if not answer_record:
            raise HTTPException(status_code=404, detail="Answer not found")
        return answer_record
    except Exception as e:
        logger.error(f"Error reading answer {answer_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{answer_id}", response_model=Answer)
async def update_answer(answer_id: int, answer_update: AnswerCreate):
    try:
        query = (
            update(answer)
            .where(answer.c.id == answer_id)
            .values(
                question_id=answer_update.question_id, 
                answer=answer_update.answer, 
                responder=answer_update.responder or "Anonymous",
                updated_at=datetime.utcnow()
            )
        )
        await database.execute(query)
        return await read_answer(answer_id)
    except Exception as e:
        logger.error(f"Error updating answer {answer_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{answer_id}")
async def delete_answer(answer_id: int):
    try:
        query = delete(answer).where(answer.c.id == answer_id)
        await database.execute(query)
        return {"message": "Answer deleted"}
    except Exception as e:
        logger.error(f"Error deleting answer {answer_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
