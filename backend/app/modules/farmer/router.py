from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import secrets

from backend.app.db.database import SessionLocal
from backend.app.modules.farmer.model import Farmer
from backend.app.modules.farmer.schema import (
    FarmerCreate,
    FarmerResponse,
    OTPRequest,
    OTPVerify,
    FarmerIdentity,
    AuthResponse
)

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


# Temporary storage for prototype authentication
otp_store = {}
session_store = {}


# =========================
# FARMER AUTHENTICATION
# =========================

@router.post("/auth/request-otp")
def request_otp(
    request: OTPRequest,
    db: Session = Depends(get_db)
):
    farmer = db.query(Farmer).filter(
        Farmer.phone == request.phone
    ).first()

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="No registered farmer found with this phone number"
        )

    # Prototype OTP
    otp = "123456"

    otp_store[request.phone] = otp

    return {
        "message": "OTP generated successfully",
        "phone": request.phone,
        "otp": otp
    }


@router.post("/auth/verify-otp", response_model=AuthResponse)
def verify_otp(
    request: OTPVerify,
    db: Session = Depends(get_db)
):
    stored_otp = otp_store.get(request.phone)

    if not stored_otp:
        raise HTTPException(
            status_code=400,
            detail="Please request an OTP first"
        )

    if request.otp != stored_otp:
        raise HTTPException(
            status_code=401,
            detail="Invalid OTP"
        )

    farmer = db.query(Farmer).filter(
        Farmer.phone == request.phone
    ).first()

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    # Create prototype session token
    access_token = secrets.token_urlsafe(32)

    farmer_identity = {
        "farmer_id": farmer.id,
        "name": farmer.name,
        "phone": farmer.phone,
        "kisan_id": farmer.kisan_id
    }

    session_store[access_token] = farmer.id

    # Remove OTP after successful verification
    del otp_store[request.phone]

    return {
        "access_token": access_token,
        "farmer": farmer_identity
    }


# =========================
# FARMER REGISTRATION
# =========================

@router.post("/", response_model=FarmerResponse)
def create_farmer(
    farmer: FarmerCreate,
    db: Session = Depends(get_db)
):
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


# =========================
# GET ALL FARMERS
# =========================

@router.get("/", response_model=list[FarmerResponse])
def get_farmers(
    db: Session = Depends(get_db)
):
    return db.query(Farmer).all()