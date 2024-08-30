from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    lang: str = "ko-KR"
    voice: str = "jihun"
    speed: str = "0.7"
    sr: str = "16000"
    sformat: str = "wav"
