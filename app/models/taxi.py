from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Taxi(Base):
    __tablename__ = "taxi"

    taxi_id = Column(Integer, primary_key=True, index=True)
    taxi_phone = Column(String(20), nullable=False)
    taxi_location = Column(String(50), nullable=False)
    taxi_type = Column(Integer, nullable=False)
