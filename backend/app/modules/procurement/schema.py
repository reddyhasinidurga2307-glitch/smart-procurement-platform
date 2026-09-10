from pydantic import BaseModel


class ProcurementCreate(BaseModel):
    procurement_id: str
    farmer_id: str
    crop_name: str
    quantity_kg: float
    quality_grade: str
    price_per_kg: float
    centre_id: str


class ProcurementResponse(ProcurementCreate):
    total_amount: float
    status: str
    created_at: str
