from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.database import get_db
from app.models.user import users
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
async def read_plans(region: str = None, category: str = None, db: Session = Depends(get_db)):
    query = select(plans_model)
    if region:
        query = query.where(plans_model.c.region == region)
    if category:
        query = query.where(plans_model.c.category == category)
    
    plans = db.execute(query).fetchall()
    
    plan_responses = []
    for plan in plans:
        plan_dict = dict(plan._mapping)
        plan_dict['images'] = json.loads(plan_dict['images']) if isinstance(plan_dict['images'], str) else plan_dict['images']
        plan_dict['itinerary'] = json.loads(plan_dict['itinerary']) if isinstance(plan_dict['itinerary'], str) else plan_dict['itinerary']
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
    itinerary_data = json.loads(itinerary)
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
        itinerary=json.dumps(itinerary_data)
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
        plan_dict['images'] = json.loads(plan_dict['images']) if isinstance(plan_dict['images'], str) else plan_dict['images']
        plan_dict['itinerary'] = json.loads(plan_dict['itinerary']) if isinstance(plan_dict['itinerary'], str) else plan_dict['itinerary']
        plan_responses.append(plans_schema.PlanResponse(**plan_dict))
    return plan_responses

@router.get("/{plan_id}", response_model=plans_schema.PlanResponse)
async def read_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(plans_model).filter(plans_model.c.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan_dict = dict(plan._mapping)
    plan_dict['images'] = json.loads(plan_dict['images']) if isinstance(plan_dict['images'], str) else plan_dict['images']
    plan_dict['itinerary'] = json.loads(plan_dict['itinerary']) if isinstance(plan_dict['itinerary'], str) else plan_dict['itinerary']
    return plans_schema.PlanResponse(**plan_dict)

@router.post("/{plan_id}/like/")
async def like_plan(plan_id: int, db: Session = Depends(get_db)):
    query = select(plans_model).where(plans_model.c.id == plan_id)
    result = db.execute(query).first()

    if not result:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = result._mapping
    new_likes = plan['likes'] + 1
    update_query = update(plans_model).where(plans_model.c.id == plan_id).values(likes=new_likes)
    db.execute(update_query)
    db.commit()
    
    return {"message": "Plan liked successfully", "likes": new_likes}

# 사용자 일정을 가져오는 새로운 엔드포인트 추가
@router.get("/user_schedules", response_model=List[plans_schema.PlanResponse])
async def read_user_schedules(userid: str = Depends(get_current_user), db: Session = Depends(get_db)):
    plans = db.query(plans_model).filter(plans_model.c.userid == userid).all()
    plan_responses = []
    for plan in plans:
        plan_dict = plan._asdict()
        plan_dict['images'] = json.loads(plan_dict['images']) if isinstance(plan_dict['images'], str) else plan_dict['images']
        plan_dict['itinerary'] = json.loads(plan_dict['itinerary']) if isinstance(plan_dict['itinerary'], str) else plan_dict['itinerary']
        plan_responses.append(plans_schema.PlanResponse(**plan_dict))
    return plan_responses
