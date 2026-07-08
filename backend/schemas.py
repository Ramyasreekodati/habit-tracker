from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# LAYER 1: Health
class HealthBase(BaseModel):
    date: str
    sleep: float
    water: int
    walk: int
    exercise: int
    meditation: int

class HealthCreate(HealthBase): pass

class HealthResponse(HealthBase):
    id: int
    class Config: from_attributes = True

# LAYER 2: Learning State
class LearningStateBase(BaseModel):
    topic: str
    difficulty: int
    importance: int
    interview_frequency: int
    pipeline_stage: str

class LearningStateCreate(LearningStateBase): pass

class LearningStateResponse(LearningStateBase):
    id: int
    class Config: from_attributes = True

# LAYER 3: Sessions
class SessionBase(BaseModel):
    date: str
    topic: str
    start_time: str
    end_time: str
    duration_minutes: int
    output_quantity: int

class SessionCreate(SessionBase): pass

class SessionResponse(SessionBase):
    id: int
    class Config: from_attributes = True

# LAYER 4: Projects
class ProjectBase(BaseModel):
    project_name: str
    feature_name: str
    status: str

class ProjectCreate(ProjectBase): pass

class ProjectResponse(ProjectBase):
    id: int
    class Config: from_attributes = True

# LAYER 5: Career
class CareerBase(BaseModel):
    date: str
    category: str
    description: str
    resume_impact: str

class CareerCreate(CareerBase): pass

class CareerResponse(CareerBase):
    id: int
    class Config: from_attributes = True
