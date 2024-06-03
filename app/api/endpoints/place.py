from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import create_or_update_place, get_place, get_all_places
from app.schemas.place import PlaceBase, Place
from app.database import get_db

router = APIRouter()

@router.post("/places/", response_model=PlaceBase) #새로운 place를 생성하거나 업데이트
def create_place_endpoint(place: PlaceBase, db: Session = Depends(get_db)):
    return create_or_update_place(db=db, place=place)

@router.get("/places/{content_id}", response_model=Place)
def read_place(content_id: int, db: Session = Depends(get_db)):
    place = get_place(db, content_id)
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return place

# @router.get("/places/", response_model=List[Place])
# def read_places(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     places = get_all_places(db=db)
#     return places

@router.get("/places/all", response_model=List[Place])
def read_all_places(db: Session = Depends(get_db)):
    return get_all_places(db)
