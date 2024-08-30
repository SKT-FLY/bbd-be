from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.taxi import Taxi
from app.models.user import User


def extract_location_part(address: str) -> str:
    # 주소에서 시, 군, 구, 읍, 면 단위 추출
    address_parts = address.split()
    # 예시: "서울특별시 중구", "경기도 수원시", "경상북도 영주시"
    for part in address_parts:
        if part.endswith("시"):
            return part
        elif part.endswith("군") or part.endswith("구"):
            return address_parts[
                address_parts.index(part) + 1
            ]  # 군, 구 다음의 읍, 면을 반환

    return None  # 해당하는 부분이 없으면 None 반환


async def find_matching_taxi(db: AsyncSession, address: str, user_id: int) -> dict:
    # user_id로 데이터베이스에서 user_type을 조회
    user_stmt = select(User).filter(User.user_id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user_type = user.user_type  # user_type을 가져옵니다.

    # 주소에서 적절한 부분 추출
    location_part = extract_location_part(address)
    if not location_part:
        return {}

    # 택시 정보 조회
    stmt = select(Taxi).filter(Taxi.taxi_location.like(f"%{location_part}%"))
    result = await db.execute(stmt)
    matching_taxis = result.scalars().all()

    taxi_dict = {}
    for taxi in matching_taxis:
        if taxi.taxi_type == 1:
            taxi_dict["type_1"] = taxi.taxi_phone
        elif taxi.taxi_type == 0:
            taxi_dict["type_0"] = taxi.taxi_phone

    if user_type == 0:
        taxi_dict = {k: v for k, v in taxi_dict.items() if k == "type_0"}

    return taxi_dict
