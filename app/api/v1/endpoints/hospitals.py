from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.session import get_db
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalOut, HospitalUpdate

router = APIRouter()


@router.get("/hospitals", response_model=List[HospitalOut])
async def get_hospitals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hospital))
    hospitals = result.scalars().all()
    return hospitals


@router.post("/hospitals/update_visits_count", response_model=HospitalOut)
async def update_or_create_hospital(
    hospital_data: HospitalUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Hospital).filter(Hospital.hospital_id == hospital_data.hospital_id)
    )
    hospital = result.scalars().first()

    if hospital:
        # 병원이 이미 존재하는 경우 visits_count를 1 증가
        hospital.visits_count = (
            hospital.visits_count + 1 if hospital.visits_count else 1
        )
    else:
        # 병원이 없는 경우 새로운 병원 추가
        hospital = Hospital(
            hospital_name=hospital_data.hospital_name,
            hospital_phone=hospital_data.hospital_phone,
            hospital_type=hospital_data.hospital_type,
            hospital_address=hospital_data.hospital_address,
            hospital_radius=hospital_data.hospital_radius,
            visits_count=1,
            user_id=hospital_data.user_id,
        )
        db.add(hospital)

    await db.commit()
    await db.refresh(hospital)
    return hospital
