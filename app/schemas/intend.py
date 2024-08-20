from pydantic import BaseModel
from typing import Optional, Union


class CommandRequest(BaseModel):
    command: str


class CommandResponseData(BaseModel):
    standardized_command: str
    result: str
    message: str
