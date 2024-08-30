from pydantic import BaseModel


class CommandRequest(BaseModel):
    user_id: int
    command: str


class CommandResponseData(BaseModel):
    standardized_command: str
    result: str
    message: str
    url: str  # 새로운 URL 필드 추가
