from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.db.database import SessionLocal
from backend.app.modules.procurement.model import ProcurementDB
from backend.app.modules.procurement.schema import (
    ProcurementCreate,
    ProcurementResponse,
)

router = APIRouter(
    prefix="/procurements",
    tags=["Procurement"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProcurementResponse)
def create_procurement(
    procurement: ProcurementCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(ProcurementDB).filter(
        ProcurementDB.procurement_id == procurement.procurement_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Procurement ID already exists"
        )

    if procurement.quantity_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    if procurement.price_per_kg < 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative"
        )

    total_amount = procurement.quantity_kg * procurement.price_per_kg

    new_procurement = ProcurementDB(
        procurement_id=procurement.procurement_id,
        farmer_id=procurement.farmer_id,
        crop_name=procurement.crop_name,
        quantity_kg=procurement.quantity_kg,
        quality_grade=procurement.quality_grade,
        price_per_kg=procurement.price_per_kg,
        total_amount=total_amount,
        centre_id=procurement.centre_id,
        status="PENDING",
        created_at=datetime.now().isoformat(),
    )

    db.add(new_procurement)
    db.commit()
    db.refresh(new_procurement)

    return new_procurement


@router.get("/", response_model=list[ProcurementResponse])
def get_procurements(db: Session = Depends(get_db)):
    return db.query(ProcurementDB).all()


@router.get("/{procurement_id}", response_model=ProcurementResponse)
def get_procurement(
    procurement_id: str,
    db: Session = Depends(get_db)
):
    procurement = db.query(ProcurementDB).filter(
        ProcurementDB.procurement_id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    return procurement
