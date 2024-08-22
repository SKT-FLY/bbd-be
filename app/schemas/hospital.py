from pydantic import BaseModel


class HospitalOut(BaseModel):
    hospital_id: int
    hospital_name: str
    hospital_phone: str
    hospital_type: str
    hospital_address: str
    hospital_radius: str
    visits_count: int

    class Config:
        orm_mode = True


class HospitalUpdate(BaseModel):
    user_id: int
    hospital_id: int
    hospital_name: str
    hospital_phone: str
    hospital_type: str
    hospital_address: str
    hospital_radius: float

    class Config:
        orm_mode = True
