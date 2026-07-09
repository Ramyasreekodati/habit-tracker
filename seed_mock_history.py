import random
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import Habit, HabitLog, HanseiReflection, SessionLocal

def seed_history():
    db = SessionLocal()
    
    # Get all habits
    habits = db.query(Habit).all()
    if not habits:
        print("No habits found. Please run app.py once to initialize habits.")
        return
        
    habit_ids = [h.id for h in habits]
    
    today = date.today()
    start_date = today - timedelta(days=180) # 6 months
    
    print("Seeding 6 months of historical data...")
    
    for i in range(180):
        current_date = (start_date + timedelta(days=i)).isoformat()
        
        # Random chance of having a good day (80%) vs bad day (20%)
        is_good_day = random.random() > 0.2
        
        for h in habits:
            # Bad habits have a 20% chance of being "completed" (which means failed) on a good day, 80% on a bad day
            if h.category == "Bad Habits":
                completed = random.random() < (0.2 if is_good_day else 0.8)
            else:
                completed = random.random() < (0.8 if is_good_day else 0.3)
                
            duration = random.choice([0, 30, 60, 90, 120]) if (completed and h.category in ["Career", "MBA"]) else 0
            
            # Check if log already exists
            existing_log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.date == current_date).first()
            if not existing_log:
                log = HabitLog(habit_id=h.id, date=current_date, completed=completed, duration=duration)
                db.add(log)
                
        # Seed Hansei Reflection
        existing_hansei = db.query(HanseiReflection).filter(HanseiReflection.date == current_date).first()
        if not existing_hansei and is_good_day and random.random() > 0.5:
            r = HanseiReflection(
                date=current_date,
                finished="Completed my daily tasks and studied.",
                distracted="A bit of social media.",
                mistake="Started working too late.",
                change_tomorrow="Wake up 30 mins earlier."
            )
            db.add(r)
            
    db.commit()
    db.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_history()
