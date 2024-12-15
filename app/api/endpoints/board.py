from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from app.models.board import board
from app.database import database
from app.schemas.board import Board

router = APIRouter()

# 게시글 생성
@router.post("/")
async def create_board(item: Board):
    query = board.insert().values(title=item.title, contents=item.contents, created_by=item.created_by)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

# 게시글 조회
@router.get("/")
async def read_boards():
    query = select(board)
    results = await database.fetch_all(query)
    return {"boards": results}

# 게시글 상세 내용 조회
@router.get("/{board_id}")
async def read_board(board_id: int):
    query = select(board).where(board.c.id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return result

# 게시글 삭제
@router.delete("/{board_id}")
async def delete_board(board_id: int):
    query = board.delete().where(board.c.id)
    await database.execute(query)
    return {"message": "Board deleted"}

# 게시글 클릭 수 증가   
@router.post("/{board_id}/click")
# async def increment_click(board_id: int):
#     query = select([board]).where(board.c.id == board_id)
#     board_data = await database.fetch_one(query)  # 'board'를 'board_data'로 변경
#     if board_data:
#         new_count = board_data['click_count'] + 1
#         update_query = board.update().where(board.c.id == board_id).values(click_count=new_count)
#         await database.execute(update_query)
#         return {"message": "Click count incremented"}
#     else:
#         raise HTTPException(status_code=404, detail="Board not found")
async def increment_click(board_id: int):
    query = select(board).where(board.c.id == board_id)
    board_instance = await database.fetch_one(query)
    if not board_instance:
        raise HTTPException(status_code=404, detail="Board not found")
    
    new_count = board_instance['click_count'] + 1
    update_query = board.update().where(board.c.id == board_id).values(click_count=new_count)
    await database.execute(update_query)
    return {"message": "Click count incremented"}


