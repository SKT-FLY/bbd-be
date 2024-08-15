from pydantic import BaseModel

class ReverseGeocodingRequest(BaseModel):
    lat: float
    lon: float
    coordType: str = "WGS84GEO"
    addressType: str = "A03"
    coordYn: str = "N"
    keyInfo: str = "N"
    newAddressExtend: str = "Y"

class ReverseGeocodingResponse(BaseModel):
    fullAddress: str

    class Config:
        orm_mode = True
