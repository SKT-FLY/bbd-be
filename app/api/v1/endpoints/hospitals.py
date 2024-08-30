from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.schemas.hospital import HospitalOut, HospitalUpdate
from app.crud.hospital import (
    get_hospitals as crud_get_hospitals,
    update_or_create_hospital as crud_update_or_create_hospital,
)

router = APIRouter()


@router.get("/hospitals", response_model=List[HospitalOut])
async def get_hospitals(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_get_hospitals(user_id, db)


@router.post("/hospitals/update_visits_count", response_model=HospitalOut)
async def update_or_create_hospital(
    hospital_data: HospitalUpdate, db: AsyncSession = Depends(get_db)
):
    return await crud_update_or_create_hospital(
        hospital_data, hospital_data.user_id, db
    )
