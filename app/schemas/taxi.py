from pydantic import BaseModel
from typing import Optional


class TaxiSearchResponse(BaseModel):
    fullAddress: str
    type_1: Optional[str] = None
    type_0: Optional[str] = None
