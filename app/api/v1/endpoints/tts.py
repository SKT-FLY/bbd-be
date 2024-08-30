import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Response, Depends
from typing import Optional, Union, List
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from dotenv import load_dotenv
from app.schemas.tts import TTSRequest
from app.db.session import get_db
from app.crud.schedule import get_schedules_by_date_and_user
from app.schemas.schedule import ScheduleOut

router = APIRouter()

# 환경 변수 로드
load_dotenv()

TTS_URL = os.environ.get("TTS_URL")
TTS_KEY = os.environ.get("TTS_KEY")
INTENT_API_URL = os.environ.get("INTENT_API_URL")
API_KEY = os.getenv("OPENAI_API_KEY_FOR_STANDARDIZATION")
client = OpenAI(api_key=API_KEY)


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


def json_to_key_value_text(schedule):
    """SQLAlchemy 객체를 키-값 텍스트 나열 형식으로 변환"""
    # SQLAlchemy 모델의 속성을 사전 형태로 변환
    schedule_dict = {
        column.name: str(getattr(schedule, column.name))
        for column in schedule.__table__.columns
    }
    return "\n".join([f"{key}: {value}" for key, value in schedule_dict.items()])


def create_gpt_prompt(schedule_list):
    """GPT에게 전달할 프롬프트 생성"""
    # 각 Schedule 객체를 순회하며, 프롬프트용 텍스트로 변환
    commands = [json_to_key_value_text(schedule) for schedule in schedule_list]
    command_str = "\n\n".join(commands)

    return [
        {
            "role": "system",
            "content": "당신은 고객의 개인 비서입니다. 다음의 예약 정보를 받아 고객에게 설명하세요. 연도 정보는 빼도 괜찮습니다. 부드럽고 친절한 말투로, 일상적인 용어를 써서 짧고 간결하게 설명하세요.",
        },
        {"role": "user", "content": command_str},
    ]


def get_gpt_response(schedule_json):
    """GPT 모델 호출 및 응답 반환"""
    messages = create_gpt_prompt(schedule_json)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


@router.get(
    "/schedules/tts/{date}", response_model=Optional[Union[List[ScheduleOut], dict]]
)
async def get_schedule_tts(date: str, user_id: int, db: AsyncSession = Depends(get_db)):
    # 1. 문자열 날짜를 datetime 객체로 변환
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식이어야 합니다.",
        )

    # 2. 주어진 날짜의 일정 가져오기
    schedules = await get_schedules_by_date_and_user(db, date_obj, user_id)
    if not schedules:
        return {"message": "일정이 없습니다"}

    # 3. 일정 데이터를 기반으로 GPT 모델을 사용해 자연어 설명 생성
    gpt_response = get_gpt_response(schedules)

    # 4. TTS API 호출 준비
    tts_request_data = TTSRequest(text=gpt_response)
    headers = {"appKey": TTS_KEY, "Content-Type": "application/json"}

    # TTS API 호출 및 음성 파일 생성
    async with httpx.AsyncClient() as client:
        tts_response = await client.post(
            TTS_URL, headers=headers, json=tts_request_data.dict()
        )

    if tts_response.status_code != 200:
        raise HTTPException(
            status_code=tts_response.status_code, detail="TTS API 요청 실패"
        )

    # 5. 음성 파일만 반환
    return Response(
        content=tts_response.content,
        media_type="audio/wav",
        headers={"Content-Disposition": 'attachment; filename="schedule.wav"'},
    )
