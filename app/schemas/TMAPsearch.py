from pydantic import BaseModel, Field
from typing import Optional, List


class POISearchParams(BaseModel):
    version: int = Field(1, description="API 버전")  # 필수 파라미터
    searchKeyword: str = Field(..., description="검색할 키워드")  # 필수 파라미터
    centerLat: float = Field(..., description="중심점의 위도")  # 필수 파라미터
    centerLon: float = Field(..., description="중심점의 경도")  # 필수 파라미터
    reqCoordType: str = Field("WGS84GEO", description="요청 좌표 유형")  # 필수 파라미터
    resCoordType: str = Field("WGS84GEO", description="응답 좌표 유형")  # 필수 파라미터
    radius: Optional[int] = Field(0, description="검색 반경 (미터 단위)")
    searchType: Optional[str] = Field("all", description="검색 유형")
    searchtypCd: Optional[str] = Field("A", description="검색 유형 코드")
    page: Optional[int] = Field(1, description="페이지 번호")
    count: Optional[int] = Field(20, description="페이지당 결과 수")
    multiPoint: Optional[str] = Field("Y", description="다중 포인트 사용 여부")
    callback: Optional[str] = Field(None, description="JSONP용 콜백 함수 이름")
    poiGroupYn: Optional[str] = Field("N", description="POI 그룹 여부")


class POI(BaseModel):
    name: str
    telNo: Optional[str]
    fullAddressRoad: str
    detailBizName: Optional[str]
    frontLat: str
    frontLon: str
    radius: Optional[str]


class POIResponse(BaseModel):
    pois: List[POI]
