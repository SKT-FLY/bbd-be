from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScheduleCreate(BaseModel):
    schedule_name: str
    schedule_start_time: datetime
    schedule_description: Optional[str]


class ScheduleUpdate(BaseModel):
    schedule_name: Optional[str]
    schedule_start_time: Optional[datetime]
    schedule_description: Optional[str]


class ScheduleOut(BaseModel):
    schedule_id: int
    schedule_name: str
    schedule_start_time: datetime
    schedule_description: Optional[str]
    user_id: int

    class Config:
        orm_mode = True


class VoiceIn(BaseModel):
    message: str
