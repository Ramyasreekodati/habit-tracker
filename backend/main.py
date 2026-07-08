from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import datetime
import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GrowthOS V10 Temporal Architecture")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.EngineUser).filter(models.EngineUser.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    return {"access_token": auth.create_access_token(data={"sub": user.username}), "token_type": "bearer"}

# --- L0: MISSION ENGINE ---
@app.get("/mission/daily", response_model=List[schemas.DailyMissionResponse])
def get_daily_missions(db: Session = Depends(get_db)):
    return db.query(models.EngineDailyMission).filter(models.EngineDailyMission.mission_date == str(datetime.date.today())).all()

@app.get("/mission/weekly", response_model=List[schemas.WeeklyTargetResponse])
def get_weekly_targets(db: Session = Depends(get_db)):
    return db.query(models.EngineWeeklyTarget).all()

@app.get("/mission/monthly", response_model=List[schemas.MonthlyGoalResponse])
def get_monthly_goals(db: Session = Depends(get_db)):
    return db.query(models.EngineMonthlyGoal).all()

@app.post("/engine/generate-schedule")
def generate_schedule(db: Session = Depends(get_db)):
    # Delete today's schedule
    db.query(models.EngineDailyMission).filter(models.EngineDailyMission.mission_date == str(datetime.date.today())).delete()
    
    # Get highest priority debt
    topics = db.query(models.EngineLearningState).filter(models.EngineLearningState.pipeline_stage != "Master").all()
    best_topic = max(topics, key=lambda t: t.importance * t.interview_frequency * t.difficulty) if topics else None
    
    tasks = [
        {"time": "05:00", "end": "06:00", "cat": "Learning", "task": f"Master {best_topic.topic if best_topic else 'Projects'}", "pri": 10},
        {"time": "08:00", "end": "09:00", "cat": "Career", "task": "Submit 2 Applications", "pri": 8},
        {"time": "16:30", "end": "17:30", "cat": "Health", "task": "Walk & Meditate", "pri": 5}
    ]
    
    for t in tasks:
        db.add(models.EngineDailyMission(mission_date=str(datetime.date.today()), start_time=t["time"], end_time=t["end"], category=t["cat"], task=t["task"], priority=t["pri"]))
    db.commit()
    return {"status": "Schedule Generated"}

@app.get("/engine/stale-tasks")
def get_stale_tasks(db: Session = Depends(get_db)):
    # Calculate tasks older than 30 days without review in 14 days
    all_topics = db.query(models.EngineLearningState).all()
    stale = []
    today = datetime.date.today()
    for t in all_topics:
        if t.created_date and t.last_reviewed_date:
            cd = datetime.datetime.strptime(t.created_date, "%Y-%m-%d").date()
            lr = datetime.datetime.strptime(t.last_reviewed_date, "%Y-%m-%d").date()
            if (today - cd).days > 30 and (today - lr).days > 14:
                stale.append(t.topic)
    return {"stale_tasks": stale}

# --- L1: HEALTH ---
@app.get("/health/", response_model=List[schemas.HealthResponse])
def get_health(db: Session = Depends(get_db)):
    return db.query(models.EngineHealth).all()

# --- L2: LEARNING STATE ---
@app.get("/learning_state/", response_model=List[schemas.LearningStateResponse])
def get_learning(db: Session = Depends(get_db)):
    return db.query(models.EngineLearningState).all()

# --- L3: SESSIONS ---
@app.post("/sessions/", response_model=schemas.SessionResponse)
def log_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = models.EngineSession(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@app.get("/sessions/", response_model=List[schemas.SessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    return db.query(models.EngineSession).all()

# --- L4: PROJECTS ---
@app.get("/projects/", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.EngineProject).all()

# --- L5: CAREER ---
@app.get("/career/", response_model=List[schemas.CareerResponse])
def get_career(db: Session = Depends(get_db)):
    return db.query(models.EngineCareer).all()
