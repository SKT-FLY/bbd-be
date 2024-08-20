from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Schedule(Base):
    __tablename__ = "schedule"

    schedule_id = Column(Integer, primary_key=True, index=True)
    schedule_name = Column(String(50), nullable=False)
    schedule_start_time = Column(DateTime, nullable=False)
    schedule_description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    user = relationship("User", back_populates="schedules")
