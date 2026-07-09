import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from app import Habit, HabitLog, SessionLocal, get_streak, MonthlyGoal, WeeklyPlan
import pandas as pd

@pytest.fixture
def db():
    db_session = SessionLocal()
    yield db_session
    db_session.close()

def test_habit_creation(db):
    h = Habit(name="Test Habit", monthly_goal=10)
    db.add(h)
    db.commit()
    
    saved = db.query(Habit).filter_by(name="Test Habit").first()
    assert saved is not None
    assert saved.monthly_goal == 10
    
    # Cleanup
    db.delete(saved)
    db.commit()

def test_streak_calculation():
    # Mock data
    today_str = date.today().isoformat()
    yest_str = (date.today() - timedelta(days=1)).isoformat()
    day_3_str = (date.today() - timedelta(days=2)).isoformat()
    future_str = (date.today() + timedelta(days=1)).isoformat()
    
    # Simple continuous streak
    data1 = pd.DataFrame([
        {"habit_id": 1, "log_date": today_str, "status": "completed"},
        {"habit_id": 1, "log_date": yest_str, "status": "completed"}
    ])
    c_streak, b_streak = get_streak(data1, 1)
    assert c_streak == 2
    assert b_streak == 2
    
    # Future dates shouldn't affect streak
    data2 = pd.DataFrame([
        {"habit_id": 1, "log_date": future_str, "status": "completed"},
        {"habit_id": 1, "log_date": today_str, "status": "completed"},
        {"habit_id": 1, "log_date": yest_str, "status": "completed"}
    ])
    c_streak, b_streak = get_streak(data2, 1)
    assert c_streak == 2
    assert b_streak == 2

    # Skipped pauses, doesn't break
    data3 = pd.DataFrame([
        {"habit_id": 1, "log_date": today_str, "status": "completed"},
        {"habit_id": 1, "log_date": yest_str, "status": "skipped"},
        {"habit_id": 1, "log_date": day_3_str, "status": "completed"}
    ])
    c_streak, b_streak = get_streak(data3, 1)
    assert c_streak == 2 # 1 today, 1 day_3. Skip is ignored.
    assert b_streak == 2

    # Missed breaks streak
    data4 = pd.DataFrame([
        {"habit_id": 1, "log_date": today_str, "status": "completed"},
        {"habit_id": 1, "log_date": yest_str, "status": "missed"},
        {"habit_id": 1, "log_date": day_3_str, "status": "completed"}
    ])
    c_streak, b_streak = get_streak(data4, 1)
    assert c_streak == 1 # Today only
    assert b_streak == 1 # The day_3 was a streak of 1

def test_database_constraints(db):
    from sqlalchemy.exc import IntegrityError
    
    # Test valid status
    h = Habit(name="Constraint Test", monthly_goal=10)
    db.add(h)
    db.commit()
    
    log = HabitLog(habit_id=h.id, log_date="2026-01-01", status="invalid_status")
    db.add(log)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    
    # Test positive goal constraint
    h_bad = Habit(name="Bad Goal", monthly_goal=-5)
    db.add(h_bad)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    
    # Cleanup
    db.delete(h)
    db.commit()
