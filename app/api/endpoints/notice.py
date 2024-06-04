from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from app.models.notice import notice
from app.database import database
from app.schemas.notice import NoticeCreate, NoticeResponse

router = APIRouter()

# 공지사항 생성
@router.post("/", response_model=NoticeResponse)
async def create_notice(item: NoticeCreate):
    query = notice.insert().values(title=item.title, content=item.content)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

# 공지사항 조회
@router.get("/")
async def read_notices():
    query = select(notice)
    results = await database.fetch_all(query)
    return {"notices": results}

# 공지사항 상세 내용 조회
@router.get("/{notice_id}")
async def read_notice(notice_id: int):
    query = select(notice).where(notice.c.id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="notice not found")
    return result

# 공지사항 수정
@router.put("/{notice_id}", response_model=NoticeResponse)
async def update_notice(notice_id: int, item: NoticeCreate):
    query = update(notice).where(notice.c.id)
    await database.execute(query)
    updated_notice = await database.fetch_one(select(notice).where(notice.c.id))
    return updated_notice

# 공지사항 삭제
@router.delete("/{notice_id}")
async def delete_notice(notice_id: int):
    query = notice.delete().where(notice.c.id)
    await database.execute(query)
    return {"message": "notice deleted"}
