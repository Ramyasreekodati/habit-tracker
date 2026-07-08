from pydantic import BaseModel
from typing import Optional

class HealthBase(BaseModel):
    date: str
    sleep: float
    water: int
    walk: int
    exercise: int
    meditation: int

class HealthCreate(HealthBase):
    pass

class HealthResponse(HealthBase):
    id: int
    class Config:
        orm_mode = True

class CareerBase(BaseModel):
    date: str
    category: str
    description: str
    resume_impact: str

class CareerCreate(CareerBase):
    pass

class CareerResponse(CareerBase):
    id: int
    class Config:
        orm_mode = True

class LearningDebtBase(BaseModel):
    topic: str
    status: str

class LearningDebtCreate(LearningDebtBase):
    pass

class LearningDebtResponse(LearningDebtBase):
    id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
