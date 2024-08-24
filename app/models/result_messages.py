from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class ResultMessage(Base):
    __tablename__ = "result_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    result = Column(String, nullable=False)
    message = Column(String, nullable=False)
    audio_data = Column(String, nullable=False)

    user = relationship("User", back_populates="result_messages")
