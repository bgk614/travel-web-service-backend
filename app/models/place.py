from sqlalchemy import Column, Integer, String
from app.database import Base

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    addr1 = Column(String(255), index=True)
    addr2 = Column(String(255), index=True)
    firstimage = Column(String(255), index=True)
    tel = Column(String(255), index=True)
    contentId = Column(Integer, unique=True, nullable=False)
    hmpg = Column(String(255))
    overview = Column(String(2000))