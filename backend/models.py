from sqlalchemy import Column, Integer, String, Float
from database import Base

class EngineHealth(Base):
    __tablename__ = "engine_health"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    sleep = Column(Float, default=0.0)
    water = Column(Integer, default=0)
    walk = Column(Integer, default=0)
    exercise = Column(Integer, default=0)
    meditation = Column(Integer, default=0)

class EngineCareer(Base):
    __tablename__ = "engine_career"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    category = Column(String)
    description = Column(String)
    resume_impact = Column(String)

class EngineLearningDebt(Base):
    __tablename__ = "engine_learning_debt"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    status = Column(String)
