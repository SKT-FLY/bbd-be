from fastapi import APIRouter, HTTPException, Response
import httpx
from dotenv import load_dotenv
import os
from app.schemas.tts import TTSRequest

router = APIRouter()

load_dotenv()

TTS_URL = os.environ.get("TTS_URL")
TTS_KEY = os.environ.get("TTS_KEY")


@router.post("/tts")
async def generate_tts(tts_request: TTSRequest):
    headers = {"appKey": TTS_KEY, "Content-Type": "application/json"}
    data = tts_request.model_dump()

    async with httpx.AsyncClient() as client:
        response = await client.post(TTS_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            return Response(
                content=response.content,
                media_type="audio/wav",
                headers={"Content-Disposition": 'attachment; filename="output.wav"'},
            )
        except httpx.RequestError:
            return {
                "message": "Request was successful, but response is not in the expected format"
            }
    else:
        raise HTTPException(status_code=response.status_code, detail="API 요청 실패")
