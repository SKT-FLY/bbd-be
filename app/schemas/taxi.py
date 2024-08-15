from pydantic import BaseModel

class TaxiSearchResponse(BaseModel):
    taxi_phone: str
    fullAddress: str
