from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union
from datetime import datetime
import os
import httpx
from dotenv import load_dotenv

from app.schemas.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate, VoiceIn
from app.crud.schedule import (
    create_schedule,
    get_schedule,
    get_schedules,
    update_schedule,
    delete_schedule,
    get_guarded_user_schedules,
    get_schedules_by_date_and_user,
)
from app.db.session import get_db


router = APIRouter()


@router.post("/schedule", response_model=ScheduleOut)
async def create_new_schedule(
    schedule: ScheduleCreate, user_id: int, db: AsyncSession = Depends(get_db)
):
    return await create_schedule(db, schedule, user_id)


@router.get("/schedule/{schedule_id}", response_model=ScheduleOut)
async def read_schedule(
    schedule_id: int, user_id: int, db: AsyncSession = Depends(get_db)
):
    db_schedule = await get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule


@router.get("/schedule", response_model=List[ScheduleOut])
async def read_schedules(
    user_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await get_schedules(db, user_id=user_id, skip=skip, limit=limit)


@router.put("/schedule/{schedule_id}", response_model=ScheduleOut)
async def update_existing_schedule(
    schedule_id: int,
    user_id: int,
    schedule: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_schedule = await update_schedule(db, schedule_id, user_id, schedule)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule


@router.delete("/schedule/{schedule_id}", response_model=ScheduleOut)
async def delete_existing_schedule(
    schedule_id: int, user_id: int, db: AsyncSession = Depends(get_db)
):
    db_schedule = await delete_schedule(db, schedule_id, user_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule


@router.get("/guardian/{guardian_id}/schedules", response_model=List[ScheduleOut])
async def read_guarded_user_schedules(
    guardian_id: int, db: AsyncSession = Depends(get_db)
):
    schedules = await get_guarded_user_schedules(db, guardian_id)
    if not schedules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No schedules found for the guarded users.",
        )
    return schedules


@router.get(
    "/schedules/date/{date}", response_model=Optional[Union[List[ScheduleOut], dict]]
)
async def read_schedules_by_date(
    date: datetime, user_id: int, db: AsyncSession = Depends(get_db)
):
    schedules = await get_schedules_by_date_and_user(db, date, user_id)
    if not schedules:
        return {"message": "일정이 없습니다"}
    return schedules


load_dotenv()

VOICESCHEDULE_API = os.getenv("VOICESCHEDULE_API")


@router.post("/voice_schedule", response_model=ScheduleCreate)
async def analyze_and_forward(request: VoiceIn):
    if not VOICESCHEDULE_API:
        raise HTTPException(
            status_code=500,
            detail="TEXT_API URL is not set in the environment variables.",
        )

    async with httpx.AsyncClient() as client:
        try:
            # 외부 API에 POST 요청 보내기
            response = await client.post(VOICESCHEDULE_API, json=request.dict())
            response.raise_for_status()  # HTTP 에러가 발생하면 예외를 발생시킴
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"External API request failed: {exc.response.text}",
            )

        response_data = response.json()

        # API 응답 데이터를 ScheduleCreate 모델에 맞게 변환
        schedule_data = {
            "schedule_name": response_data[
                "description"
            ],  # 예시로 VoiceIn의 message 필드를 schedule_name에 매핑
            "schedule_start_time": response_data["when"],
            "schedule_description": request.message,
        }

        # JSON 응답을 ScheduleCreate 모델로 직접 변환하여 반환
        return ScheduleCreate(**schedule_data)
