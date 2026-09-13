from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.modules.farmer.model import Farmer
from backend.app.modules.farmer.schema import FarmerCreate, FarmerResponse

router = APIRouter(
    prefix="/farmers",
    tags=["Farmers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=FarmerResponse)
def create_farmer(farmer: FarmerCreate, db: Session = Depends(get_db)):
    new_farmer = Farmer(
      name=farmer.name,
      phone=farmer.phone,
      crop=farmer.crop,
      quantity=farmer.quantity,
      location=farmer.location,
      kisan_id=farmer.kisan_id
    )

    db.add(new_farmer)
    db.commit()
    db.refresh(new_farmer)

    return new_farmer


@router.get("/", response_model=list[FarmerResponse])
def get_farmers(db: Session = Depends(get_db)):
    return db.query(Farmer).all()