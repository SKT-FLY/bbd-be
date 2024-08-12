from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(20), nullable=False)

    hospitals = relationship("Hospital", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
