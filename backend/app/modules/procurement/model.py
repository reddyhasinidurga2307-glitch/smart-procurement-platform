from sqlalchemy import Column, Integer, String, Float
from backend.app.db.database import Base


class ProcurementDB(Base):
    __tablename__ = "procurements"

    id = Column(Integer, primary_key=True, index=True)

    procurement_id = Column(String, unique=True, nullable=False)
    farmer_id = Column(String, nullable=False)
    crop_name = Column(String, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    quality_grade = Column(String, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    centre_id = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(String, nullable=False)
