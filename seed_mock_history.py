import random
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import calendar

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import Habit, HabitLog, SessionLocal

def seed_history():
    db = SessionLocal()
    
    habits = db.query(Habit).all()
    if not habits:
        print("No habits found. Please run app.py once to initialize.")
        return
        
    today = date.today()
    # Go back 2 full months
    start_date = today.replace(day=1) - timedelta(days=60)
    end_date = today
    
    print("Seeding ~60 days of Final V1 data...")
    
    curr = start_date
    while curr <= end_date:
        current_date_str = curr.isoformat()
        is_good_day = random.random() > 0.3
        
        for h in habits:
            existing_log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.log_date == current_date_str).first()
            if not existing_log:
                if is_good_day:
                    status = random.choices(["completed", "missed", "skipped", ""], weights=[0.8, 0.1, 0.05, 0.05])[0]
                else:
                    status = random.choices(["completed", "missed", "skipped", ""], weights=[0.2, 0.6, 0.1, 0.1])[0]
                
                # Make today have mostly "" so user can fill it
                if curr == end_date:
                    status = ""
                    
                log = HabitLog(habit_id=h.id, log_date=current_date_str, status=status)
                db.add(log)
                
        curr += timedelta(days=1)
                
    db.commit()
    db.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_history()
