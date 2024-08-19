from fastapi import APIRouter, HTTPException, Depends, Query
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import os
from app.db.session import get_db
from app.schemas.reversegeocoding import (
    ReverseGeocodingRequest,
    ReverseGeocodingResponse,
)
from app.schemas.taxi import TaxiSearchResponse
from app.crud.taxi import find_matching_taxi

router = APIRouter()

load_dotenv()

RG_URL = os.environ.get("RG_URL")
TMAP_API_KEY = os.environ.get("TMAP_API_KEY")


async def fetch_reverse_geocoding(request: ReverseGeocodingRequest) -> dict:
    headers = {"Accept": "application/json", "appKey": TMAP_API_KEY}
    params = request.dict()

    async with httpx.AsyncClient() as client:
        response = await client.get(RG_URL, headers=headers, params=params)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="TMap API에서 데이터를 가져오는 중 오류가 발생했습니다.",
            )

        return response.json()


@router.post("/taxi-search/", response_model=TaxiSearchResponse)
async def taxi_number_search(
    request: ReverseGeocodingRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    user_type: int = Query(
        ..., description="택시 번호 검색 동작을 결정하는 사용자 유형"
    ),
):
    data = await fetch_reverse_geocoding(request)
    full_address = data.get("addressInfo", {}).get("fullAddress")

    if not full_address:
        raise HTTPException(
            status_code=404, detail="응답에서 전체 주소를 찾을 수 없습니다."
        )

    matching_taxi_dict = await find_matching_taxi(db, full_address, user_type)

    if not matching_taxi_dict:
        raise HTTPException(status_code=404, detail="일치하는 택시를 찾을 수 없습니다.")

    # `None` 값이 있으면 필드 자체를 제거하거나, 원하는 형태로 값을 설정합니다.
    response_data = TaxiSearchResponse(
        fullAddress=full_address,
        type_1=matching_taxi_dict.get("type_1"),
        type_0=matching_taxi_dict.get("type_0"),
    )

    return response_data
