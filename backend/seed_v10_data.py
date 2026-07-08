import sqlite3
import datetime
import random
import os

def seed_db():
    db_path = '../growthos.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed legacy database.")

    # Recreate tables via FastAPI models
    import database
    import models
    import auth
    
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    
    print("Creating admin user...")
    admin = models.EngineUser(username="admin", hashed_password=auth.get_password_hash("password123"))
    db.add(admin)

    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=35)
    
    # Layer 0: Mission
    db.add(models.EngineWeeklyTarget(week_start=str(today - datetime.timedelta(days=today.weekday())), week_end=str(today + datetime.timedelta(days=6-today.weekday())), category="SQL Problems", target=15, completed=6))
    db.add(models.EngineWeeklyTarget(week_start=str(today - datetime.timedelta(days=today.weekday())), week_end=str(today + datetime.timedelta(days=6-today.weekday())), category="Git Commits", target=20, completed=11))
    
    db.add(models.EngineMonthlyGoal(month="July 2026", goal="Complete GenAI Course", target_value="100%", current_value="62%", deadline="2026-07-31"))
    db.add(models.EngineMonthlyGoal(month="July 2026", goal="GrowthOS MVP", target_value="Deployment", current_value="45%", deadline="2026-07-31"))

    # Layer 2: Learning State
    db.add(models.EngineLearningState(topic="Window Functions", difficulty=9, importance=10, interview_frequency=8, pipeline_stage="Learn", created_date=str(today)))
    db.add(models.EngineLearningState(topic="LangChain Memory", difficulty=6, importance=8, interview_frequency=6, pipeline_stage="Implement", created_date=str(today)))
    # Stale task
    db.add(models.EngineLearningState(topic="Pandas GroupBy", difficulty=3, importance=9, interview_frequency=10, pipeline_stage="Learn", created_date=str(last_month), last_reviewed_date=str(last_month + datetime.timedelta(days=5))))

    # Layer 3: Sessions
    for i in range(15):
        date = today - datetime.timedelta(days=random.randint(0, 30))
        s = models.EngineSession(session_date=str(date), topic="SQL Practice", start_time="05:00", end_time="06:30", duration_minutes=90, output_quantity=random.randint(1, 5), energy_before=8, energy_after=6)
        db.add(s)
        
    db.commit()
    db.close()
    print("GrowthOS V10 Successfully Seeded!")

if __name__ == "__main__":
    seed_db()
