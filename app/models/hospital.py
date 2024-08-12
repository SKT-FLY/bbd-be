from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Hospital(Base):
    __tablename__ = "hospital"

    hospital_id = Column(Integer, primary_key=True, index=True)
    hospital_name = Column(String(50), nullable=False)
    hospital_phone = Column(String(20), nullable=False)
    hospital_type = Column(String(50), nullable=False)
    hospital_address = Column(String(100), nullable=False)
    hospital_radius = Column(String(10), nullable=False)
    visits_count = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    user = relationship("User", back_populates="hospitals")
    schedules = relationship("Schedule", back_populates="hospital")
