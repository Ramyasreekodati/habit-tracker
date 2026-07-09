import random
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import Habit, HabitLog, EnergyLog, SessionLocal

def seed_history():
    db = SessionLocal()
    
    habits = db.query(Habit).all()
    if not habits:
        print("No habits found. Please run app.py once to initialize.")
        return
        
    today = date.today()
    start_date = today - timedelta(days=30) # 1 month
    
    print("Seeding 30 days of V1 data...")
    
    for i in range(30):
        current_date = (start_date + timedelta(days=i)).isoformat()
        
        # Energy
        morning_e = random.choice(["High", "High", "Medium", "Low"])
        afternoon_e = random.choice(["High", "Medium", "Medium", "Low"])
        night_e = random.choice(["High", "Medium", "Low", "Low"])
        
        existing_e = db.query(EnergyLog).filter(EnergyLog.date == current_date).first()
        if not existing_e:
            elog = EnergyLog(date=current_date, morning_energy=morning_e, afternoon_energy=afternoon_e, night_energy=night_e)
            db.add(elog)
            
        is_good_day = random.random() > 0.3
        
        for h in habits:
            existing_log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.date == current_date).first()
            if not existing_log:
                if h.category in ["AI Core", "MBA"]:
                    planned = h.default_planned_time
                    completed = random.random() < (0.8 if is_good_day else 0.4)
                    if completed:
                        actual = planned
                        friction = None
                    else:
                        actual = int(planned * random.uniform(0.1, 0.7))
                        friction = random.choice(["Too difficult", "Too boring", "Distracted", "Too large", "No clear next step"])
                    tod = random.choice(["Morning", "Afternoon", "Night"])
                else:
                    planned = 0
                    actual = 0
                    completed = random.random() < (0.9 if is_good_day else 0.5)
                    friction = "Distracted" if not completed else None
                    tod = "Morning"
                
                log = HabitLog(habit_id=h.id, date=current_date, completed=completed, planned_duration=planned, duration=actual, time_of_day=tod, friction_reason=friction)
                db.add(log)
                
    db.commit()
    db.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_history()
