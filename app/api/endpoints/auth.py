from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from app.models.users import users
from app.database import database, get_db
from app.schemas.users import UserCreate, UserResponse
from app.schemas.auth import *
from app.utils.jwt import verify_access_token
from passlib.context import CryptContext
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from app.utils.jwt import create_access_token, verify_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter()

verification_codes = {}

def load_secrets():
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    return secrets

secrets = load_secrets()
SECRET_KEY = secrets['SECRET_KEY']

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 사용자 조회 함수
def get_user(db: Session, userid: str = None, email: str = None):
    query = select(users)
    if userid:
        query = query.where(users.c.userid == userid)
    if email:
        query = query.where(users.c.email == email)
    
    result = db.execute(query).first()
    if result:
        return dict(result._mapping)
    return None

# 사용자 인증 함수
def authenticate_user(db: Session, userid: str, password: str):
    user = get_user(db, userid)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token, SECRET_KEY)
        if payload is None:
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_query = select(users).where(users.c.userid == user_id)
    result = db.execute(user_query).first()
    if result is None:
        raise credentials_exception
    user = dict(result._mapping)
    return user["userid"]


# 로그인 엔드포인트
@router.post("/login/", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.userid, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["userid"]}, secret_key=SECRET_KEY, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 현재 사용자 정보 조회 엔드포인트
@router.get("/users/me/", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

# 아이디 중복 확인 엔드포인트
@router.post("/check-userid/")
async def check_userid(request: CheckUserIdRequest, db: Session = Depends(get_db)):
    query = select(users).where(users.c.userid == request.userid)
    result = await database.fetch_one(query)
    if result:
        return {"available": False}
    return {"available": True}

# 닉네임 중복 확인 엔드포인트
@router.post("/check-nickname/")
async def check_nickname(request: CheckNicknameRequest, db: Session = Depends(get_db)):
    query = select(users).where(users.c.nickname == request.nickname)
    result = await database.fetch_one(query)
    if result:
        return {"available": False}
    return {"available": True}

# 회원가입 엔드포인트
@router.post("/signup/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 아이디 중복 확인
    query = select(users).where(users.c.userid == user.userid)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="UserId already registered")
    
    # 닉네임 중복 확인
    query = select(users).where(users.c.nickname == user.nickname)
    existing_nickname = await database.fetch_one(query)
    if existing_nickname:
        raise HTTPException(status_code=400, detail="Nickname already registered")
    
    try:
        hashed_password = get_password_hash(user.password)
        query = insert(users).values(
            userid=user.userid,
            password=hashed_password,
            nickname=user.nickname,
            name=user.name,
            phone=user.phone,
            email=user.email,
            address=user.address
        )
        last_record_id = await database.execute(query)
        return {**user.dict(), "id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 인증번호 요청 엔드포인트
@router.post("/send-code/")
async def send_code(request: EmailRequest, db: Session = Depends(get_db)):
    if request.name:
        # 아이디 찾기 요청
        user = get_user(db, email=request.email)
        if not user or user["name"] != request.name:
            raise HTTPException(status_code=400, detail="제공된 이름과 이메일이 등록된 정보와 일치하지 않습니다")
    elif request.userid:
        # 비밀번호 찾기 요청
        user = get_user(db, userid=request.userid)
        if not user or user["email"] != request.email:
            raise HTTPException(status_code=400, detail="제공된 아이디와 이메일이 등록된 정보와 일치하지 않습니다")
    else:
        raise HTTPException(status_code=400, detail="요청 본문에 적절한 필드가 포함되어 있지 않습니다")
    
    secrets = load_secrets()
    verification_code = ''.join(random.choices(string.digits, k=6))
    verification_codes[request.email] = verification_code
    
    sender_email = secrets['SENDER_EMAIL']
    password = secrets['EMAIL_PASSWORD']
    receiver_email = request.email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification Code"
    message["From"] = f"TravelMaker <{sender_email}>"
    message["To"] = receiver_email

    text = f"Your verification code is {verification_code}"
    html = f"""\
    <html>
      <body>
        <p>Hi,<br>
           Your verification code is <strong>{verification_code}</strong>.
        </p>
      </body>
    </html>
    """
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return {"message": "Verification code sent successfully via email", "code": verification_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 인증번호 확인 엔드포인트
@router.post("/verify-code/")
async def verify_code(request: VerifyCodeRequest):
    if request.email not in verification_codes:
        raise HTTPException(status_code=404, detail="Email address not found")

    if verification_codes[request.email] != request.verificationCode:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # 인증 코드 검증 후 삭제
    del verification_codes[request.email]
    return {"success": True}
    
# 아이디 찾기 엔드포인트
@router.post("/find-id/")
async def find_id(request: FindIDRequest, db: Session = Depends(get_db)):
    query = select(users).where(users.c.name == request.name, users.c.email == request.email)
    result = db.execute(query).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = dict(result._mapping)
    return {"userid": user["userid"]}

# 인증 엔드포인트
@router.post("/verify-user/")
async def verify_user(request: VerifyUserRequest, db: Session = Depends(get_db)):
    if request.email not in verification_codes:
        raise HTTPException(status_code=404, detail="Email address not found")
    
    if verification_codes[request.email] != request.verificationCode:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Verify user details
    query = select(users).where(users.c.userid == request.userid, users.c.email == request.email)
    result = db.execute(query).first()
    
    if not result:
        raise HTTPException(status_code=400, detail="User details do not match")
    
    # Verification successful, delete the verification code
    del verification_codes[request.email]
    user = dict(result._mapping)
    return {"success": True}

# 비밀번호 설정 엔드포인트
@router.post("/reset-password/")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    query = select(users).where(users.c.userid == request.userid)
    result = db.execute(query).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = get_password_hash(request.newPassword)
    query = update(users).where(users.c.userid == request.userid).values(password=hashed_password)
    db.execute(query)
    db.commit()
    return {"success": True}
