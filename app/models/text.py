from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Text(Base):
    __tablename__ = "text"

    text_id = Column(Integer, primary_key=True, index=True)
    text_content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    user = relationship("User", back_populates="texts")
