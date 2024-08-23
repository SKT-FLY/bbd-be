from pydantic import BaseModel
from typing import Optional


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    source: Optional[str]
    date: Optional[str]
    message_type: Optional[str]
    summary: Optional[str]
