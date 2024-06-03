# from sqlalchemy import Column, Integer, String
# from app.database import Base

# class Place(Base):
#     __tablename__ = "places"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255), index=True)
#     addr1 = Column(String(255), index=True)
#     addr2 = Column(String(255), index=True)
#     firstimage = Column(String(255), index=True)
#     tel = Column(String(255), index=True)
#     contentId = Column(Integer, unique=True, nullable=False)
#     hmpg = Column(String(255))
#     overview = Column(String(2000))
from sqlalchemy import Table, Column, Integer, String, MetaData, Text, TIMESTAMP, text

metadata = MetaData()

place = Table(
    "places",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("addr1", String(255), nullable=True),
    Column("addr2", String(255), nullable=True),
    Column("firstimage", String(255), nullable=True),
    Column("tel", String(255), nullable=True),
    Column("contentId", Integer, unique=True, nullable=False),
    Column("hmpg", String(255), nullable=True),
    Column("overview", Text, nullable=True),
    Column("created_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True),
    Column("updated_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True, onupdate=text('CURRENT_TIMESTAMP'))
)
