from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, update, insert
from sqlalchemy.orm import Session
from app.models.user import user
from app.database import get_db, database
from app.schemas.user import UserCreate, UserResponse, LoginRequest, PhoneRequest, UserUpdate, VerifyCodeRequest, FindIDRequest, VerifyUserRequest, ResetPasswordRequest
from app.utils import get_password_hash, verify_password
import random
import string

router = APIRouter()

verification_codes = {}

@router.get("/", response_model=UserResponse)
async def read_user():
    query = select(user)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.put("/", response_model=UserResponse)
async def update_user(user_data: UserUpdate, db: Session = Depends(get_db)):
    query = select(user).where(user.c.id == user_data.id)
    db_user = await database.fetch_one(query)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    update_query = update(user).where(user.c.id == user_data.id).values(**update_data)
    await database.execute(update_query)
    
    updated_user_query = select(user).where(user.c.id == user_data.id)
    updated_user = await database.fetch_one(updated_user_query)
    return updated_user

def get_user(db: Session, userid: str):
    query = select(user).where(user.c.userid == userid)
    return db.execute(query).first()

def authenticate_user(db: Session, userid: str, password: str):
    query = select(user).where(user.c.userid == userid)
    db_user = db.execute(query).first()
    if not db_user:
        return False
    if not verify_password(password, db_user.password):
        return False
    return db_user

@router.post("/signup/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user_data.password)
    query = insert(user).values(
        userid=user_data.userid,
        password=hashed_password,
        nickname=user_data.nickname,
        name=user_data.name,
        birthdate=user_data.birthdate,
        phone=user_data.phone,
        email=user_data.email
    )
    try:
        last_record_id = await database.execute(query)
        return {**user_data.dict(), "id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login/", response_model=UserResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, request.userid, request.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return db_user  # UserResponse 모델로 반환

@router.post("/send-code/")
async def send_code(request: PhoneRequest):
    verification_code = ''.join(random.choices(string.digits, k=6))
    verification_codes[request.phone] = verification_code
    print(f"Sent code {verification_code} to phone number {request.phone}")
    return {"message": "Verification code sent"}

@router.post("/verify-code/")
async def verify_code(request: VerifyCodeRequest):
    if request.phone not in verification_codes:
        raise HTTPException(status_code=404, detail="Phone number not found")

    if verification_codes[request.phone] != request.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    del verification_codes[request.phone]
    return {"success": True}

@router.post("/find-id/")
async def find_id(request: FindIDRequest, db: Session = Depends(get_db)):
    query = select(user).where(user.c.name == request.name, user.c.phone == request.phone)
    db_user = await db.execute(query).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"userId": db_user.userid}

@router.post("/verify-user/")
async def verify_user(request: VerifyUserRequest, db: Session = Depends(get_db)):
    if request.phone not in verification_codes:
        raise HTTPException(status_code=404, detail="Phone number not found")

    if verification_codes[request.phone] != request.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    query = select(user).where(user.c.userid == request.id, user.c.name == request.name, user.c.phone == request.phone)
    db_user = await db.execute(query).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User details do not match")

    del verification_codes[request.phone]
    return {"success": True}

@router.post("/reset-password/")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    query = select(user).where(user.c.userid == request.id)
    db_user = await db.execute(query).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(request.new_password)
    update_query = update(user).values(password=hashed_password).where(user.c.id == db_user.id)
    await db.execute(update_query)
    
    updated_user_query = select(user).where(user.c.id == db_user.id)
    updated_user = await db.execute(updated_user_query)
    
    return {"success": True}

@router.post("/check-userid/")
async def check_userid(userid: str, db: Session = Depends(get_db)):
    query = select(user).where(user.c.userid == userid)
    db_user = await database.fetch_one(query)
    if db_user:
        return {"exists": True}
    else:
        return {"exists": False}