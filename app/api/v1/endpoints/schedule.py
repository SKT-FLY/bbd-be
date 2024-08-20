from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union
from datetime import datetime

from app.schemas.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate
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
    schedule: ScheduleCreate, db: AsyncSession = Depends(get_db)
):
    return await create_schedule(db, schedule)


@router.get("/schedule/{schedule_id}", response_model=ScheduleOut)
async def read_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    db_schedule = await get_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule


@router.get("/schedule", response_model=List[ScheduleOut])
async def read_schedules(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await get_schedules(db, skip=skip, limit=limit)


@router.put("/schedule/{schedule_id}", response_model=ScheduleOut)
async def update_existing_schedule(
    schedule_id: int, schedule: ScheduleUpdate, db: AsyncSession = Depends(get_db)
):
    db_schedule = await update_schedule(db, schedule_id, schedule)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule


@router.delete("/schedule/{schedule_id}", response_model=ScheduleOut)
async def delete_existing_schedule(
    schedule_id: int, db: AsyncSession = Depends(get_db)
):
    db_schedule = await delete_schedule(db, schedule_id)
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
