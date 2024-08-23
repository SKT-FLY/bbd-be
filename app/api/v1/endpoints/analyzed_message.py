from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv
import os
from app.schemas.text import MessageRequest, MessageResponse

router = APIRouter()

load_dotenv()

TEXT_API = os.getenv("TEXT_API")


@router.post("/analyze_and_forward", response_model=MessageResponse)
async def analyze_and_forward(request: MessageRequest):
    async with httpx.AsyncClient() as client:
        try:
            # 외부 API에 POST 요청 보내기
            response = await client.post(TEXT_API, json=request.dict())
            response.raise_for_status()  # HTTP 에러가 발생하면 예외를 발생시킴
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="External API request failed",
            )

        # 응답을 받아서 클라이언트에 그대로 반환
        return response.json()
