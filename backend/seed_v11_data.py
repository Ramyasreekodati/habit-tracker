import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db: Session = SessionLocal()
    
    # Check if we already have habits
    if db.query(models.Habit).count() > 0:
        print("Habits already exist. Skipping seed.")
        db.close()
        return

    habits = [
        # Career
        {"name": "Python", "category": "Career"},
        {"name": "SQL", "category": "Career"},
        {"name": "DSA", "category": "Career"},
        {"name": "GenAI", "category": "Career"},
        {"name": "Project Work", "category": "Career"},
        
        # MBA
        {"name": "Classes", "category": "MBA"},
        {"name": "Assignments", "category": "MBA"},
        
        # Discipline
        {"name": "Meditation", "category": "Discipline"},
        {"name": "Housework", "category": "Discipline"},
        {"name": "Sleep", "category": "Discipline"},
        {"name": "Exercise", "category": "Discipline"},
        
        # Bad Habits
        {"name": "Phone overuse", "category": "Bad Habits"},
        {"name": "Procrastination", "category": "Bad Habits"},
        {"name": "Overthinking", "category": "Bad Habits"},
        {"name": "Late sleeping", "category": "Bad Habits"},
    ]

    print("Seeding Habits...")
    for h in habits:
        db.add(models.Habit(**h))
    
    db.commit()
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed_data()
