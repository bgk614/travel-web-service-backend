from sqlalchemy.orm import Session
from app.models.place import Place
from app.schemas.place import PlaceBase

def create_or_update_place(db: Session, place: PlaceBase):
    db_place = db.query(Place).filter(Place.contentId == place.contentId).first()
    if db_place is None:
        db_place = Place(
            title=place.title,
            addr1=place.addr1,
            addr2=place.addr2,
            firstimage=place.firstimage,
            tel=place.tel,
            contentId=place.contentId,
            hmpg=place.hmpg,
            overview=place.overview
        )
    else:
        db_place.title = place.title
        db_place.addr1 = place.addr1
        db_place.addr2 = place.addr2
        db_place.firstimage = place.firstimage
        db_place.tel = place.tel
        db_place.hmpg = place.hmpg
        db_place.overview = place.overview

    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

def get_place(db: Session, content_id: int):
    return db.query(Place).filter(Place.contentId == content_id).first()

def get_all_places(db: Session):
    return db.query(Place).all()
