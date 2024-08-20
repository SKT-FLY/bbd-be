from sqlalchemy import Column, Integer, String
from app.db.base import Base


class ResultMessage(Base):
    __tablename__ = "result_messages"

    id = Column(Integer, primary_key=True, index=True)
    result = Column(String, unique=True, index=True)
    message = Column(String)
