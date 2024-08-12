from pydantic import BaseModel, EmailStr


class TTSRequest(BaseModel):
    text: str
    lang: str = "ko-KR"
    voice: str = "seohyun"
    speed: str = "1.5"
    sr: str = "16000"
    sformat: str = "wav"
