from sqlalchemy import Column, Integer, String, Float
from backend.app.db.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    crop = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    kisan_id = Column(String, nullable=True, unique=True)
    status = Column(String, default="active")