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
    
    print("Generating Layer 1: Health...")
    for i in range(30):
        date = today - datetime.timedelta(days=i)
        sleep = round(random.uniform(6.0, 8.5), 1)
        h = models.EngineHealth(date=str(date), sleep=sleep, water=random.randint(6,10), walk=45, exercise=0, meditation=0)
        db.add(h)
        
    print("Generating Layer 2: Learning State...")
    db.add(models.EngineLearningState(topic="Window Functions", difficulty=9, importance=10, interview_frequency=8, pipeline_stage="Learn"))
    db.add(models.EngineLearningState(topic="LangChain RAG", difficulty=6, importance=8, interview_frequency=6, pipeline_stage="Implement"))
    db.add(models.EngineLearningState(topic="Pandas GroupBy", difficulty=3, importance=9, interview_frequency=10, pipeline_stage="Master"))

    print("Generating Layer 3: Sessions...")
    for i in range(15):
        date = today - datetime.timedelta(days=random.randint(0, 30))
        s = models.EngineSession(date=str(date), topic="SQL Practice", start_time="10:00", end_time="11:30", duration_minutes=90, output_quantity=5)
        db.add(s)
        
    print("Generating Layer 5: Career...")
    c = models.EngineCareer(date=str(today), category="Project Feature", description="Built RAG chatbot using LangChain", resume_impact="Developed a Retrieval-Augmented Generation system using LangChain and vector embeddings for document question answering.")
    db.add(c)

    db.commit()
    db.close()
    print("GrowthOS V9 Successfully Seeded!")

if __name__ == "__main__":
    seed_db()
