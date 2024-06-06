from pydantic import BaseModel
from typing import Optional

class PlaceBase(BaseModel):
    title: str
    addr1: str
    addr2: str
    firstimage: str
    tel: str
    contentId: int
    hmpg: Optional[str]
    overview: Optional[str]
    sigunguCode: Optional[int]

class PlaceCreate(PlaceBase):
    pass

class Place(PlaceBase):
    id: int

    class Config:
        from_attributes = True

class PlaceUpdate(BaseModel):
    detail_text: str
