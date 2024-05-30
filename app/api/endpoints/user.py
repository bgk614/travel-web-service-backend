from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from app.models.user import user
from app.database import database
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("/", response_model=UserResponse)
async def read_user():
    query = select(user)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.put("/")
async def update_user(user_data: UserCreate):
    # 기존 사용자 조회 (id 사용)
    query = select(user).where(user.c.id == user_data.id)
    db_user = await database.fetch_one(query)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # userid 중복 확인
    if user_data.userid != db_user.userid:
        duplicate_query = select(user).where(user.c.userid == user_data.userid)
        duplicate_user = await database.fetch_one(duplicate_query)
        if duplicate_user:
            raise HTTPException(status_code=400, detail="User ID already exists")

    update_data = {
        "userid": user_data.userid,
        "nickname": user_data.nickname,
        "name": user_data.name,
        "phone": user_data.phone,
        "email": user_data.email,
        "birthdate": user_data.birthdate
    }

    if user_data.password:
        update_data["password"] = user_data.password

    update_query = update(user).values(update_data).where(user.c.id == db_user.id)
    await database.execute(update_query)
    return {**user_data.dict(exclude_unset=True), "id": db_user.id}
