from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# L0: MISSION ENGINE
class DailyMissionBase(BaseModel):
    mission_date: str
    start_time: str
    end_time: str
    category: str
    task: str
    status: str
    priority: int
    completed_at: Optional[str] = None

class DailyMissionResponse(DailyMissionBase):
    id: int
    class Config: from_attributes = True

class WeeklyTargetBase(BaseModel):
    week_start: str
    week_end: str
    category: str
    target: int
    completed: int

class WeeklyTargetResponse(WeeklyTargetBase):
    id: int
    class Config: from_attributes = True

class MonthlyGoalBase(BaseModel):
    month: str
    goal: str
    target_value: str
    current_value: str
    deadline: str
    status: str

class MonthlyGoalResponse(MonthlyGoalBase):
    id: int
    class Config: from_attributes = True

# L1: HEALTH
class HealthBase(BaseModel):
    date: str
    sleep: float
    water: int
    walk: int
    exercise: int
    meditation: int

class HealthResponse(HealthBase):
    id: int
    class Config: from_attributes = True

# L2: LEARNING STATE
class LearningStateBase(BaseModel):
    topic: str
    difficulty: int
    importance: int
    interview_frequency: int
    pipeline_stage: str
    created_date: str
    target_completion_date: Optional[str] = None
    actual_completion_date: Optional[str] = None
    last_reviewed_date: Optional[str] = None
    next_review_date: Optional[str] = None

class LearningStateResponse(LearningStateBase):
    id: int
    class Config: from_attributes = True

# L3: SESSIONS
class SessionBase(BaseModel):
    session_date: str
    topic: str
    start_time: str
    end_time: str
    duration_minutes: int
    energy_before: int
    energy_after: int
    output_quantity: int

class SessionCreate(SessionBase): pass

class SessionResponse(SessionBase):
    id: int
    class Config: from_attributes = True

# L4: PROJECTS
class ProjectBase(BaseModel):
    project_name: str
    feature_name: str
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    status: str

class ProjectResponse(ProjectBase):
    id: int
    class Config: from_attributes = True

# L5: CAREER
class CareerBase(BaseModel):
    date: str
    category: str
    description: str
    resume_impact: str

class CareerResponse(CareerBase):
    id: int
    class Config: from_attributes = True
