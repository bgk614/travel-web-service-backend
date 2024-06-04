# from pydantic import BaseModel
# from typing import Optional

# class TourBase(BaseModel):
#     title: str
#     addr1: Optional[str] = None
#     addr2: Optional[str] = None
#     firstimage: Optional[str] = None
#     tel: Optional[str] = None

# class TourCreate(TourBase):
#     pass

# class Tour(TourBase):
#     id: int

#     class Config:
#         from_attributes = True

# class Tour(BaseModel):
#     id: int
#     name: str
#     address: str
#     description: str
#     image: str
#     clicks: int