from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, CheckConstraint, UniqueConstraint, Index, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Many-to-Many relationship table for Habit and Tag
habit_tag_association = Table(
    'habit_tags', Base.metadata,
    Column('habit_id', Integer, ForeignKey('habits.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    habits = relationship("Habit", secondary=habit_tag_association, back_populates="tags")


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        CheckConstraint('monthly_goal > 0', name='check_goal_positive'),
        CheckConstraint('difficulty IN (1, 2, 3)', name='check_difficulty_range'),
    )
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    monthly_goal = Column(Integer, default=20)
    reward = Column(String)
    frequency_type = Column(String, default="daily")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # New fields
    difficulty = Column(Integer, default=1) # 1: Easy, 2: Medium, 3: Hard
    notes = Column(String, default="")
    
    tags = relationship("Tag", secondary=habit_tag_association, back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (
        CheckConstraint("status IN ('', 'completed', 'missed', 'skipped')", name='check_valid_status'),
        UniqueConstraint('habit_id', 'log_date', name='uq_habit_date'),
        Index('idx_logs_habit_date', 'habit_id', 'log_date')
    )
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"))
    log_date = Column(Date, index=True)
    status = Column(String, default="")
    note = Column(String)
    missed_reason = Column(String, default="") 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    habit = relationship("Habit", back_populates="logs")


class AnnualGoal(Base):
    __tablename__ = "annual_goals"
    __table_args__ = (
        UniqueConstraint('target_year', 'title', name='uq_annual_goal_year_title'),
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
    )
    id = Column(Integer, primary_key=True, index=True)
    target_year = Column(Integer, index=True)
    title = Column(String)
    description = Column(String, default="")
    progress = Column(Integer, default=0) # 0-100%
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonthlyGoal(Base):
    __tablename__ = "monthly_goals"
    __table_args__ = (
        UniqueConstraint('year_month', 'goal_text', name='uq_monthly_goal_text'),
        Index('idx_year_month', 'year_month'),
    )
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String, index=True) # YYYY-MM
    goal_text = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    __table_args__ = (
        UniqueConstraint('year_month', 'week_number', 'task_text', name='uq_weekly_plan_task'),
    )
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String, index=True)
    week_number = Column(Integer) # 1-5
    task_text = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonthlyReflection(Base):
    __tablename__ = "monthly_reflections"
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String, index=True, unique=True)
    wins = Column(String, default="")
    improvements = Column(String, default="")
    notes = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyJournal(Base):
    __tablename__ = "daily_journals"
    __table_args__ = (
        CheckConstraint('energy BETWEEN 1 AND 10', name='check_energy_range'),
        CheckConstraint('focus_score BETWEEN 1 AND 10', name='check_focus_range'),
        CheckConstraint('stress_score BETWEEN 1 AND 10', name='check_stress_range'),
        CheckConstraint('sleep_hours >= 0 AND sleep_hours <= 24', name='check_sleep_range'),
    )
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, unique=True)
    mood = Column(String, default="") # Emoji or text
    energy = Column(Integer, default=0) # 1-10
    sleep_hours = Column(Float, default=0.0) 
    focus_score = Column(Integer, default=0) # 1-10
    stress_score = Column(Integer, default=0) # 1-10
    notes = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WeeklyReview(Base):
    __tablename__ = "weekly_reviews"
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, index=True, unique=True) # Monday of the week
    wins = Column(String, default="")
    failures = Column(String, default="")
    distractions = Column(String, default="")
    next_week_priority = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
