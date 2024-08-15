from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.taxi import Taxi

def extract_location_part(address: str) -> str:
    # 주소에서 시, 군, 구, 읍, 면 단위 추출
    address_parts = address.split()
    
    # 예시: "서울특별시 중구", "경기도 수원시", "경상북도 영주시"
    for part in address_parts:
        if part.endswith("시"):
            return part
        elif part.endswith("군") or part.endswith("구"):
            return address_parts[address_parts.index(part) + 1]  # 군, 구 다음의 읍, 면을 반환

    return None  # 해당하는 부분이 없으면 None 반환

async def find_matching_taxi(db: AsyncSession, address: str) -> str:
    # 주소에서 적절한 부분 추출
    location_part = extract_location_part(address)

    if not location_part:
        return None

    # 비동기 세션을 사용하여 쿼리 실행
    stmt = select(Taxi).filter(Taxi.taxi_location.like(f"%{location_part}%"))
    result = await db.execute(stmt)
    matching_taxi = result.scalars().first()

    if matching_taxi:
        return matching_taxi.taxi_phone
    else:
        return None
