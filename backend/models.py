from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class EngineUser(Base):
    __tablename__ = "engine_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# L0: MISSION ENGINE
class EngineDailyMission(Base):
    __tablename__ = "engine_daily_mission"
    id = Column(Integer, primary_key=True, index=True)
    mission_date = Column(String, index=True)
    start_time = Column(String)
    end_time = Column(String)
    category = Column(String)
    task = Column(String)
    status = Column(String, default="Pending")
    priority = Column(Integer, default=5)
    completed_at = Column(String, nullable=True)

class EngineWeeklyTarget(Base):
    __tablename__ = "engine_weekly_targets"
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(String, index=True)
    week_end = Column(String)
    category = Column(String)
    target = Column(Integer)
    completed = Column(Integer, default=0)

class EngineMonthlyGoal(Base):
    __tablename__ = "engine_monthly_goals"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, index=True)
    goal = Column(String)
    target_value = Column(String) # e.g. '100%' or '60'
    current_value = Column(String, default='0')
    deadline = Column(String)
    status = Column(String, default="In Progress")

# L1: HEALTH
class EngineHealth(Base):
    __tablename__ = "engine_health"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    sleep = Column(Float, default=0.0)
    water = Column(Integer, default=0)
    walk = Column(Integer, default=0)
    exercise = Column(Integer, default=0)
    meditation = Column(Integer, default=0)

# L2: LEARNING STATE
class EngineLearningState(Base):
    __tablename__ = "engine_learning_state"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, unique=True, index=True)
    difficulty = Column(Integer, default=5)
    importance = Column(Integer, default=5)
    interview_frequency = Column(Integer, default=5)
    pipeline_stage = Column(String, default="Learn")
    created_date = Column(String)
    target_completion_date = Column(String, nullable=True)
    actual_completion_date = Column(String, nullable=True)
    last_reviewed_date = Column(String, nullable=True)
    next_review_date = Column(String, nullable=True)

# L3: SESSIONS
class EngineSession(Base):
    __tablename__ = "engine_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_date = Column(String, index=True)
    topic = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    duration_minutes = Column(Integer)
    energy_before = Column(Integer, default=5)
    energy_after = Column(Integer, default=5)
    output_quantity = Column(Integer)

# L4: PROJECTS
class EngineProject(Base):
    __tablename__ = "engine_projects"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    feature_name = Column(String)
    planned_start_date = Column(String, nullable=True)
    planned_end_date = Column(String, nullable=True)
    actual_end_date = Column(String, nullable=True)
    status = Column(String, default="🔄 In Progress")

# L5: CAREER
class EngineCareer(Base):
    __tablename__ = "engine_career"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    category = Column(String)
    description = Column(String)
    resume_impact = Column(String)
