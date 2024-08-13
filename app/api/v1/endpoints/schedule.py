from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate
from app.crud.schedule import (
    create_schedule,
    get_schedule,
    get_schedules,
    update_schedule,
    delete_schedule,
)
from app.db.session import get_db


router = APIRouter()


@router.post("/schedule", response_model=ScheduleOut)
async def create_new_schedule(schedule: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    return await create_schedule(db, schedule)

@router.get("/schedule/{schedule_id}", response_model=ScheduleOut)
async def read_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    db_schedule = await get_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.get("/schedule", response_model=List[ScheduleOut])
async def read_schedules(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_schedules(db, skip=skip, limit=limit)

@router.put("/schedule/{schedule_id}", response_model=ScheduleOut)
async def update_existing_schedule(schedule_id: int, schedule: ScheduleUpdate, db: AsyncSession = Depends(get_db)):
    db_schedule = await update_schedule(db, schedule_id, schedule)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.delete("/schedule/{schedule_id}", response_model=ScheduleOut)
async def delete_existing_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    db_schedule = await delete_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule
