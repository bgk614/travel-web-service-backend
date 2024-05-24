from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.models.users import users
from app.database import database
from app.schemas.users import UserCreate, UserResponse

router = APIRouter()

@router.get("/", response_model=UserResponse)
async def read_users():
    query = select(users)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.put("/")
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

    if user.password:
        update_data["password"] = user.password

    update_query = users.update().values(update_data).where(users.c.id == db_user.id)
    await database.execute(update_query)
    return {**user.dict(exclude_unset=True), "id": db_user.id}