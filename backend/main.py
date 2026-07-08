from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GrowthOS Execution Engine API")

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
        for key, value in health.dict().items():
            setattr(db_health, key, value)
    else:
        db_health = models.EngineHealth(**health.dict())
        db.add(db_health)
    db.commit()
    db.refresh(db_health)
    return db_health

@app.get("/health/", response_model=List[schemas.HealthResponse])
def get_health_logs(skip: int = 0, limit: int = 7, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineHealth).order_by(models.EngineHealth.date.desc()).offset(skip).limit(limit).all()

# --- LAYER 2: LEARNING DEBT ---
@app.post("/learning_debt/", response_model=schemas.LearningDebtResponse)
def add_debt(debt: schemas.LearningDebtCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_debt = models.EngineLearningDebt(**debt.dict())
    db.add(db_debt)
    db.commit()
    db.refresh(db_debt)
    return db_debt

@app.get("/learning_debt/", response_model=List[schemas.LearningDebtResponse])
def get_debt(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineLearningDebt).all()

@app.put("/learning_debt/{debt_id}", response_model=schemas.LearningDebtResponse)
def update_debt(debt_id: int, status: str, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_debt = db.query(models.EngineLearningDebt).filter(models.EngineLearningDebt.id == debt_id).first()
    if not db_debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    db_debt.status = status
    db.commit()
    db.refresh(db_debt)
    return db_debt

# --- LAYER 3: CAREER ---
@app.post("/career/", response_model=schemas.CareerResponse)
def log_career_output(output: schemas.CareerCreate, db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    db_output = models.EngineCareer(**output.dict())
    db.add(db_output)
    db.commit()
    db.refresh(db_output)
    return db_output

@app.get("/career/", response_model=List[schemas.CareerResponse])
def get_career_outputs(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    return db.query(models.EngineCareer).order_by(models.EngineCareer.id.desc()).limit(30).all()

# --- EXECUTION ENGINE ---
@app.get("/next-task/")
def get_next_task(db: Session = Depends(get_db), current_user: models.EngineUser = Depends(auth.get_current_user)):
    # Simple logic: Find a high-priority unmastered learning debt
    next_debt = db.query(models.EngineLearningDebt).filter(models.EngineLearningDebt.status == "❌ Not Mastered").first()
    
    if next_debt:
        return {
            "current_task": next_debt.topic,
            "expected_duration": "45 minutes",
            "reason": "This is an unresolved item on your Learning Debt list.",
            "career_impact": "High",
            "resume_impact": "Medium",
            "difficulty": "High"
        }
    else:
        return {
            "current_task": "Build Project Feature",
            "expected_duration": "90 minutes",
            "reason": "Learning debt is clear. Time to execute.",
            "career_impact": "Maximum",
            "resume_impact": "High",
            "difficulty": "Medium"
        }
