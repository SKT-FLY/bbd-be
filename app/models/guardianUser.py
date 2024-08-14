from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class GuardianUser(Base):
    __tablename__ = "guardian_user"

    guardian_user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    guardian_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    guardian = relationship(
        "User", foreign_keys=[guardian_id], back_populates="guardians"
    )
    user = relationship("User", foreign_keys=[user_id], back_populates="guarded_users")
