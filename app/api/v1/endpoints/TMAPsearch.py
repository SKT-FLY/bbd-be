from fastapi import FastAPI, Query, HTTPException, APIRouter, Depends
import httpx
from dotenv import load_dotenv
import os
from app.schemas.TMAPsearch import POI, POIResponse, POISearchParams

router = APIRouter()

load_dotenv()

TMAP_URL = os.environ.get("TMAP_URL")
TMAP_KEY = os.environ.get("TMAP_KEY")


@router.get("/pois", response_model=POIResponse)
async def get_pois(params: POISearchParams = Depends()):
    headers = {"Accept": "application/json", "appKey": TMAP_KEY}

    # POISearchParams 모델을 딕셔너리로 변환하고 None 값을 필터링
    query_params = {k: v for k, v in params.dict().items() if v is not None}

    async with httpx.AsyncClient() as client:
        response = await client.get(TMAP_URL, headers=headers, params=query_params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API 요청 실패. 상태 코드: {response.status_code}, 응답 내용: {response.text}",
        )

    data = response.json()

    # POI 리스트에서 원하는 필드만 추출
    pois = [
        POI(
            name=poi["name"],
            telNo=poi.get("telNo"),
            fullAddressRoad=poi["newAddressList"]["newAddress"][0]["fullAddressRoad"],
            detailBizName=poi.get("detailBizName"),
            frontLat=poi["frontLat"],
            frontLon=poi["frontLon"],
            radius=poi.get("radius"),
        )
        for poi in data["searchPoiInfo"]["pois"]["poi"]
    ]

    return POIResponse(pois=pois)
