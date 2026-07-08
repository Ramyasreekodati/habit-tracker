from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class EngineUser(Base):
    __tablename__ = "engine_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# LAYER 1: Health
class EngineHealth(Base):
    __tablename__ = "engine_health"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    sleep = Column(Float, default=0.0)
    water = Column(Integer, default=0)
    walk = Column(Integer, default=0)
    exercise = Column(Integer, default=0)
    meditation = Column(Integer, default=0)

# LAYER 2: Learning State
class EngineLearningState(Base):
    __tablename__ = "engine_learning_state"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, unique=True, index=True)
    difficulty = Column(Integer, default=5) # 1-10
    importance = Column(Integer, default=5) # 1-10
    interview_frequency = Column(Integer, default=5) # 1-10
    pipeline_stage = Column(String, default="Learn") # Learn -> Implement -> Test -> Review -> Master

# LAYER 3: Sessions
class EngineSession(Base):
    __tablename__ = "engine_sessions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    topic = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    duration_minutes = Column(Integer)
    output_quantity = Column(Integer) # e.g. 4 problems solved

# LAYER 4: Projects
class EngineProject(Base):
    __tablename__ = "engine_projects"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    feature_name = Column(String)
    status = Column(String, default="🔄 In Progress")

# LAYER 5: Career
class EngineCareer(Base):
    __tablename__ = "engine_career"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    category = Column(String)
    description = Column(String)
    resume_impact = Column(String)
