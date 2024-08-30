from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from fastapi import HTTPException
from typing import List
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from app.models.guardianUser import GuardianUser


async def create_schedule(db: AsyncSession, schedule: ScheduleCreate, user_id: int):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid user_id: User does not exist"
        )

    # Schedule 생성
    db_schedule = Schedule(**schedule.dict(), user_id=user_id)
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def get_schedule(db: AsyncSession, schedule_id: int, user_id: int):
    result = await db.execute(
        select(Schedule).where(
            Schedule.schedule_id == schedule_id, Schedule.user_id == user_id
        )
    )
    return result.scalars().first()


async def get_schedules(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Schedule).where(Schedule.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_schedule(
    db: AsyncSession, schedule_id: int, user_id: int, schedule: ScheduleUpdate
):
    db_schedule = await get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None
    for key, value in schedule.dict(exclude_unset=True).items():
        setattr(db_schedule, key, value)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def delete_schedule(db: AsyncSession, schedule_id: int, user_id: int):
    db_schedule = await get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.delete(db_schedule)
    await db.commit()
    return db_schedule


async def get_guarded_user_schedules(
    db: AsyncSession, guardian_id: int
) -> List[ScheduleOut]:
    result = await db.execute(
        select(GuardianUser).filter(GuardianUser.guardian_id == guardian_id)
    )
    guardian_relationships = result.scalars().all()

    if not guardian_relationships:
        return []

    guarded_user_ids = [rel.user_id for rel in guardian_relationships]

    result = await db.execute(
        select(Schedule).filter(Schedule.user_id.in_(guarded_user_ids))
    )
    schedules = result.scalars().all()

    return [
        ScheduleOut(
            schedule_id=schedule.schedule_id,
            schedule_name=schedule.schedule_name,
            schedule_start_time=schedule.schedule_start_time,
            schedule_description=schedule.schedule_description,
            user_id=schedule.user_id,
        )
        for schedule in schedules
    ]


async def get_schedules_by_date_and_user(
    db: AsyncSession, date: datetime, user_id: int
) -> List[Schedule]:
    start_of_day = datetime.combine(date.date(), datetime.min.time())
    end_of_day = datetime.combine(date.date(), datetime.max.time())

    result = await db.execute(
        select(Schedule).where(
            Schedule.user_id == user_id,
            Schedule.schedule_start_time >= start_of_day,
            Schedule.schedule_start_time <= end_of_day,
        )
    )
    return result.scalars().all()
