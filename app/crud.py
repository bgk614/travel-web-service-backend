from sqlalchemy.orm import Session
from app.models.place import place
from app.schemas.place import PlaceBase
from sqlalchemy import select, update, insert

def create_or_update_place(db: Session, place_data: PlaceBase):
    stmt = select(place).where(place.c.contentId == place_data.contentId)
    db_place = db.execute(stmt).fetchone()

    if db_place:
        stmt = (
            update(place)
            .where(place.c.contentId == place_data.contentId)
            .values(**place_data.dict())
        )
    else:
        stmt = insert(place).values(**place_data.dict())

    db.execute(stmt)
    db.commit()

def get_place(db: Session, content_id: int):
    stmt = select(place).where(place.c.contentId == content_id)
    return db.execute(stmt).fetchone()

def get_all_places(db: Session):
    stmt = select(place)
    return db.execute(stmt).fetchall()

# from sqlalchemy.orm import Session
# from app.models.place import Place
# from app.schemas.place import PlaceBase

# def create_or_update_place(db: Session, place: PlaceBase):
#     db_place = db.query(Place).filter(Place.contentId == place.contentId).first()
#     if db_place is None:
#         db_place = Place(
#             title=place.title,
#             addr1=place.addr1,
#             addr2=place.addr2,
#             firstimage=place.firstimage,
#             tel=place.tel,
#             contentId=place.contentId,
#             hmpg=place.hmpg,
#             overview=place.overview
#         )
#     else:
#         db_place.title = place.title
#         db_place.addr1 = place.addr1
#         db_place.addr2 = place.addr2
#         db_place.firstimage = place.firstimage
#         db_place.tel = place.tel
#         db_place.hmpg = place.hmpg
#         db_place.overview = place.overview

#     db.add(db_place)
#     db.commit()
#     db.refresh(db_place)
#     return db_place

# def get_place(db: Session, content_id: int):
#     return db.query(Place).filter(Place.contentId == content_id).first()

# def get_all_places(db: Session):
#     return db.query(Place).all()
