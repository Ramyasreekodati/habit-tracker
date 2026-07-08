from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GrowthOS V9 5-Layer Execution Engine")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.EngineUser).filter(models.EngineUser.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- LAYER 1: HEALTH ---
@app.post("/health/", response_model=schemas.HealthResponse)
def log_health(health: schemas.HealthCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_health = db.query(models.EngineHealth).filter(models.EngineHealth.date == health.date).first()
    if db_health:
        for key, value in health.model_dump().items():
            setattr(db_health, key, value)
    else:
        db_health = models.EngineHealth(**health.model_dump())
        db.add(db_health)
    db.commit()
    db.refresh(db_health)
    return db_health

@app.get("/health/", response_model=List[schemas.HealthResponse])
def get_health_logs(skip: int = 0, limit: int = 7, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineHealth).order_by(models.EngineHealth.date.desc()).offset(skip).limit(limit).all()

# --- LAYER 2: LEARNING STATE ---
@app.post("/learning_state/", response_model=schemas.LearningStateResponse)
def add_learning_state(state: schemas.LearningStateCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_state = models.EngineLearningState(**state.model_dump())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

@app.get("/learning_state/", response_model=List[schemas.LearningStateResponse])
def get_learning_state(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineLearningState).all()

@app.put("/learning_state/{topic_id}/pipeline", response_model=schemas.LearningStateResponse)
def update_pipeline(topic_id: int, pipeline_stage: str, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_state = db.query(models.EngineLearningState).filter(models.EngineLearningState.id == topic_id).first()
    if not db_state:
        raise HTTPException(status_code=404, detail="Topic not found")
    db_state.pipeline_stage = pipeline_stage
    db.commit()
    db.refresh(db_state)
    return db_state

# --- LAYER 3: SESSIONS ---
@app.post("/sessions/", response_model=schemas.SessionResponse)
def log_session(session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_session = models.EngineSession(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@app.get("/sessions/", response_model=List[schemas.SessionResponse])
def get_sessions(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineSession).order_by(models.EngineSession.id.desc()).limit(20).all()

# --- LAYER 4: PROJECTS ---
@app.post("/projects/", response_model=schemas.ProjectResponse)
def add_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_proj = models.EngineProject(**project.model_dump())
    db.add(db_proj)
    db.commit()
    db.refresh(db_proj)
    return db_proj

@app.get("/projects/", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineProject).all()

# --- LAYER 5: CAREER ---
@app.post("/career/", response_model=schemas.CareerResponse)
def log_career_output(output: schemas.CareerCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_output = models.EngineCareer(**output.model_dump())
    db.add(db_output)
    db.commit()
    db.refresh(db_output)
    return db_output

@app.get("/career/", response_model=List[schemas.CareerResponse])
def get_career_outputs(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineCareer).order_by(models.EngineCareer.id.desc()).limit(30).all()

# --- ALGORITHMIC ENGINES ---
@app.get("/engine/next-task")
def get_next_task(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    topics = db.query(models.EngineLearningState).filter(models.EngineLearningState.pipeline_stage != "Master").all()
    if not topics:
        return {"current_task": "Execute Project Milestones", "reason": "No unmastered learning debt."}
    
    # priority = importance * interview_frequency * difficulty
    best_topic = max(topics, key=lambda t: t.importance * t.interview_frequency * t.difficulty)
    return {
        "current_task": best_topic.topic,
        "pipeline_stage": best_topic.pipeline_stage,
        "priority_score": best_topic.importance * best_topic.interview_frequency * best_topic.difficulty,
        "reason": f"Highest priority unmastered topic."
    }

@app.get("/engine/opportunity-cost")
def get_opportunity_cost(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    sessions = db.query(models.EngineSession).all()
    if not sessions:
        return {"message": "2 hours social media = 8 missed problems (estimated)"}
    
    total_minutes = sum(s.duration_minutes for s in sessions if s.duration_minutes > 0)
    total_outputs = sum(s.output_quantity for s in sessions if s.output_quantity > 0)
    
    if total_minutes == 0:
        return {"message": "2 hours social media = 8 missed problems (estimated)"}
        
    rate_per_hour = (total_outputs / total_minutes) * 60
    return {"message": f"2 hours social media = {round(rate_per_hour * 2, 1)} missed problems (calculated from your history)"}

@app.post("/engine/generate-resume")
def generate_resume_bullet(input_text: dict, current_user: models.EngineUser = Depends(auth.get_current_user)):
    # Mock AI Transformer. In a real system, this hits OpenAI/Gemini.
    text = input_text.get("text", "").lower()
    if "rag" in text or "langchain" in text:
        return {"resume_bullet": "Developed a Retrieval-Augmented Generation system using LangChain and vector embeddings for document question answering."}
    elif "sql" in text:
        return {"resume_bullet": "Optimized complex data pipelines using advanced SQL window functions and CTEs, significantly reducing query latency."}
    else:
        return {"resume_bullet": f"Engineered scalable solutions for {text} utilizing modern software architecture principles."}
