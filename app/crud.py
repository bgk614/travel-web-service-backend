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

