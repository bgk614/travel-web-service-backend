from pydantic import BaseModel
from typing import List, Optional

class ItineraryItem(BaseModel):
    day: int
    time: str
    activity: str

class PlanCreate(BaseModel):
    title: str
    description: str
    region: str
    category: str
    userid: str
    images: Optional[List[str]] = []
    itinerary: List[ItineraryItem]  # 일정표를 리스트 형식으로 저장

class PlanResponse(BaseModel):
    id: int
    title: str
    description: str
    region: str
    category: str
    userid: str
    images: List[str]
    likes: int
    itinerary: List[ItineraryItem]

    class Config:
        orm_mode = True
