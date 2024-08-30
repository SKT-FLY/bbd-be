from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(20), nullable=False)
    user_type = Column(Integer, nullable=False)
    user_tts = Column(Integer, nullable=False)

    hospitals = relationship("Hospital", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    texts = relationship("Text", back_populates="user")
    guardians = relationship(
        "GuardianUser",
        foreign_keys="[GuardianUser.guardian_id]",
        back_populates="guardian",
    )
    guarded_users = relationship(
        "GuardianUser", foreign_keys="[GuardianUser.user_id]", back_populates="user"
    )

    result_messages = relationship("ResultMessage", back_populates="user")
