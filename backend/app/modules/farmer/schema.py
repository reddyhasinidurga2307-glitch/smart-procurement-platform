from pydantic import BaseModel


class FarmerCreate(BaseModel):
    name: str
    phone: str
    crop: str
    quantity: float
    location: str
    kisan_id: str | None = None


class FarmerResponse(FarmerCreate):
    id: int
    status: str

    class Config:
        from_attributes = True
class OTPRequest(BaseModel):
    phone: str


class OTPVerify(BaseModel):
    phone: str
    otp: str


class FarmerIdentity(BaseModel):
    farmer_id: int
    name: str
    phone: str
    kisan_id: str | None = None
class AuthResponse(BaseModel):
    access_token: str
    farmer: FarmerIdentity