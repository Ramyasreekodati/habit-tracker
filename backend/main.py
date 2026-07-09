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
import os
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GrowthOS V10 Temporal Architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# --- V11 PHASE 1: SURVIVAL DASHBOARD ---
@app.get("/habits/", response_model=List[schemas.HabitResponse])
def get_habits(db: Session = Depends(get_db)):
    return db.query(models.Habit).all()

@app.post("/habits/", response_model=schemas.HabitResponse)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    db_habit = models.Habit(**habit.model_dump())
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@app.get("/habit_logs/", response_model=List[schemas.HabitLogResponse])
def get_habit_logs(date: str = None, db: Session = Depends(get_db)):
    query = db.query(models.HabitLog)
    if date:
        query = query.filter(models.HabitLog.date == date)
    return query.all()

@app.post("/habit_logs/", response_model=schemas.HabitLogResponse)
def log_habit(log: schemas.HabitLogCreate, db: Session = Depends(get_db)):
    db_log = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == log.habit_id,
        models.HabitLog.date == log.date
    ).first()
    if db_log:
        db_log.completed = log.completed
        db_log.duration = log.duration
    else:
        db_log = models.HabitLog(**log.model_dump())
        db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# --- V11 PHASE 3: HANSEI REFLECTION ---
@app.get("/hansei/", response_model=List[schemas.HanseiReflectionResponse])
def get_hansei_reflections(db: Session = Depends(get_db)):
    return db.query(models.HanseiReflection).order_by(models.HanseiReflection.date.desc()).all()

@app.post("/hansei/", response_model=schemas.HanseiReflectionResponse)
def log_hansei(reflection: schemas.HanseiReflectionCreate, db: Session = Depends(get_db)):
    db_reflection = db.query(models.HanseiReflection).filter(models.HanseiReflection.date == reflection.date).first()
    if db_reflection:
        db_reflection.finished = reflection.finished
        db_reflection.distracted = reflection.distracted
        db_reflection.mistake = reflection.mistake
        db_reflection.change_tomorrow = reflection.change_tomorrow
    else:
        db_reflection = models.HanseiReflection(**reflection.model_dump())
        db.add(db_reflection)
    db.commit()
    db.refresh(db_reflection)
    return db_reflection

# --- V11 PHASE 4: AI ANALYSIS LAYER ---
@app.get("/ai/analyze", response_model=schemas.AIAnalysisResponse)
def analyze_data(db: Session = Depends(get_db)):
    logs = db.query(models.HabitLog).all()
    reflections = db.query(models.HanseiReflection).all()
    
    total_logs = len(logs)
    if total_logs == 0:
        return {
            "patterns": ["Not enough data to detect patterns yet. Keep logging!"],
            "risks": ["System abandonment risk is high if you do not track your habits."],
            "recommendations": ["Start by checking off one habit today to build momentum."]
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        # Fallback to mock if no key
        return {
            "patterns": [
                "You complete Python 90% of the time.",
                "You complete DSA only 35% of the time.",
                "Most DSA failures happen after 7 PM."
            ],
            "risks": [
                "Your sleep has dropped below 6 hours for 5 days.",
                "Your productivity dropped by 22%.",
                "You may experience burnout."
            ],
            "recommendations": [
                "Move DSA to morning hours.",
                "Reduce study sessions longer than 2 hours.",
                "Add a break after SQL sessions.",
                "(To get real AI insights, add your OPENAI_API_KEY to backend/.env)"
            ]
        }
        
    # Make the real OpenAI call
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Simple prompt assembly
    data_summary = f"Total logs: {len(logs)}, Total reflections: {len(reflections)}\n"
    for r in reflections[-3:]:
        data_summary += f"Date: {r.date}\nFinished: {r.finished}\nDistracted: {r.distracted}\nMistake: {r.mistake}\nChange: {r.change_tomorrow}\n"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a productivity AI coach analyzing a user's habits. Return ONLY JSON with three keys: 'patterns' (list of strings), 'risks' (list of strings), 'recommendations' (list of strings)."},
                {"role": "user", "content": f"Analyze this recent habit and reflection data:\n{data_summary}"}
            ]
        )
        content = response.choices[0].message.content
        ai_data = json.loads(content)
        return {
            "patterns": ai_data.get("patterns", ["Analyzed successfully."]),
            "risks": ai_data.get("risks", ["None detected."]),
            "recommendations": ai_data.get("recommendations", ["Keep up the good work!"])
        }
    except Exception as e:
        return {
            "patterns": ["Failed to connect to OpenAI."],
            "risks": [str(e)],
            "recommendations": ["Check your API key and connection."]
        }

