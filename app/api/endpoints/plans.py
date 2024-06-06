from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models.users import users
from app.models.plans import plans as plans_model
from app.schemas import plans as plans_schema
import shutil
import json
from typing import List
from app.utils.jwt import verify_access_token
from fastapi.security import OAuth2PasswordBearer
from app.api.endpoints.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/current_user")
async def get_current_user_endpoint(userid: str = Depends(get_current_user)):
    return {"userid": userid}

@router.get("/", response_model=List[plans_schema.PlanResponse])
async def read_plans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    plans = db.query(plans_model).offset(skip).limit(limit).all()
    
    # 응답 데이터를 리스트 형식으로 변환
    plan_responses = []
    for plan in plans:
        plan_dict = plan._asdict()  # SQLAlchemy 객체를 딕셔너리로 변환
        plan_dict['images'] = json.loads(plan_dict['images']) if plan_dict['images'] else []
        plan_dict['itinerary'] = json.loads(plan_dict['itinerary']) if plan_dict['itinerary'] else []
        plan_responses.append(plans_schema.PlanResponse(**plan_dict))
    
    return plan_responses

@router.post("/", response_model=plans_schema.PlanResponse)
async def create_plan(
    title: str = Form(...),
    description: str = Form(...),
    region: str = Form(...),
    category: str = Form(...),
    userid: str = Depends(get_current_user),
    itinerary: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    itinerary_data = json.loads(itinerary)  # JSON 문자열을 파싱하여 파이썬 객체로 변환
    image_urls = []

    for image in images:
        image_path = f"app/uploads/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_urls.append(image_path)

    new_plan = plans_model.insert().values(
        title=title,
        description=description,
        region=region,
        category=category,
        userid=userid,
        images=json.dumps(image_urls),
        likes=0,
        itinerary=json.dumps(itinerary_data)  # 일정표를 JSON 형식으로 저장
    )
    last_record_id = await db.execute(new_plan)
    db.commit()

    return {
        "id": last_record_id,
        "title": title,
        "description": description,
        "region": region,
        "category": category,
        "userid": userid,
        "images": image_urls,
        "likes": 0,
        "itinerary": itinerary_data
    }

@router.get("/schedules", response_model=List[plans_schema.PlanResponse])
async def read_schedules(userid: str, db: Session = Depends(get_db)):
    plans = db.query(plans_model).filter(plans_model.c.userid == userid).all()
    plan_responses = []
    for plan in plans:
        plan_dict = plan._asdict()
        plan_dict['images'] = json.loads(plan_dict['images']) if plan_dict['images'] else []
        plan_dict['itinerary'] = json.loads(plan_dict['itinerary']) if plan_dict['itinerary'] else []
        plan_responses.append(plans_schema.PlanResponse(**plan_dict))
    return plan_responses
