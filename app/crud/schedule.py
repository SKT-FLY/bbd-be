from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.hospital import Hospital
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate

async def create_schedule(db: AsyncSession, schedule: ScheduleCreate):
    user = await db.get(User, schedule.user_id)
    hospital = await db.get(Hospital, schedule.hospital_id)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user_id: User does not exist")
    
    if not hospital:
        raise HTTPException(status_code=400, detail="Invalid hospital_id: Hospital does not exist")
    
    # Schedule 생성
    db_schedule = Schedule(**schedule.dict())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

async def get_schedule(db: AsyncSession, schedule_id: int):
    return await db.get(Schedule, schedule_id)

async def get_schedules(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Schedule).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_schedule(db: AsyncSession, schedule_id: int, schedule: ScheduleUpdate):
    db_schedule = await get_schedule(db, schedule_id)
    if not db_schedule:
        return None
    for key, value in schedule.dict(exclude_unset=True).items():
        setattr(db_schedule, key, value)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

async def delete_schedule(db: AsyncSession, schedule_id: int):
    db_schedule = await get_schedule(db, schedule_id)
    if db_schedule:
        await db.delete(db_schedule)
        await db.commit()
    return db_schedule
