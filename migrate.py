import os
import shutil
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import new models
from database import Base, engine as new_engine, SessionLocal as NewSession
from models import Habit, HabitLog, MonthlyGoal, WeeklyPlan, MonthlyReflection, DailyJournal, WeeklyReview, AnnualGoal, Tag

def migrate():
    # 1. Backup existing DB
    base_dir = os.path.dirname(os.path.abspath(__file__))
    old_db_path = os.path.join(base_dir, 'growthos.db')
    backup_db_path = os.path.join(base_dir, 'growthos_old_backup.db')
    
    if not os.path.exists(old_db_path):
        print("No existing database found. Initializing new database.")
        Base.metadata.create_all(bind=new_engine)
        return
        
    print(f"Backing up old database to {backup_db_path}")
    shutil.copy2(old_db_path, backup_db_path)
    
    # 2. Connect to old DB using raw sqlite/sqlalchemy without strict models
    old_engine = create_engine(f"sqlite:///{backup_db_path}")
    OldSession = sessionmaker(bind=old_engine)
    old_session = OldSession()
    
    # 3. Create new tables in the new database (clears and recreates)
    # Since we can't delete the file if it's open, let's close new_engine first
    new_engine.dispose()
    try:
        os.remove(old_db_path)
    except FileNotFoundError:
        pass
    
    # Recreate the engine and tables
    Base.metadata.create_all(bind=new_engine)
    new_session = NewSession()
    
    try:
        # Migrate Habits
        print("Migrating Habits...")
        old_habits = old_session.execute(text("SELECT * FROM habits")).fetchall()
        for h in old_habits:
            created_at_dt = h.created_at
            if isinstance(created_at_dt, str):
                try:
                    created_at_dt = datetime.fromisoformat(created_at_dt)
                except ValueError:
                    created_at_dt = datetime.strptime(created_at_dt, '%Y-%m-%d %H:%M:%S.%f')

            new_habit = Habit(
                id=h.id,
                name=h.name,
                category=h.category,
                monthly_goal=h.monthly_goal,
                reward=h.reward,
                frequency_type=h.frequency_type,
                created_at=created_at_dt,
                is_active=h.is_active,
                display_order=h.display_order,
                difficulty=1, # Default
                notes=""
            )
            new_session.add(new_habit)
        new_session.commit()

        # Migrate HabitLogs
        print("Migrating HabitLogs...")
        old_logs = old_session.execute(text("SELECT * FROM habit_logs")).fetchall()
        for l in old_logs:
            log_date_dt = datetime.fromisoformat(l.log_date).date() if l.log_date else None
            
            new_log = HabitLog(
                id=l.id,
                habit_id=l.habit_id,
                log_date=log_date_dt,
                status=l.status,
                note=l.note,
                missed_reason=""
            )
            new_session.add(new_log)
        new_session.commit()

        # Migrate Monthly Goals
        print("Migrating MonthlyGoals...")
        old_mgoals = old_session.execute(text("SELECT * FROM monthly_goals")).fetchall()
        for mg in old_mgoals:
            new_mg = MonthlyGoal(
                id=mg.id,
                year_month=mg.year_month,
                goal_text=mg.goal_text,
                completed=mg.completed
            )
            new_session.add(new_mg)
        new_session.commit()

        # Migrate Weekly Plans
        print("Migrating WeeklyPlans...")
        old_wplans = old_session.execute(text("SELECT * FROM weekly_plans")).fetchall()
        for wp in old_wplans:
            new_wp = WeeklyPlan(
                id=wp.id,
                year_month=wp.year_month,
                week_number=wp.week_number,
                task_text=wp.task_text,
                completed=wp.completed
            )
            new_session.add(new_wp)
        new_session.commit()

        # Migrate Monthly Reflections
        print("Migrating MonthlyReflections...")
        old_mrefs = old_session.execute(text("SELECT * FROM monthly_reflections")).fetchall()
        for mr in old_mrefs:
            new_mr = MonthlyReflection(
                id=mr.id,
                year_month=mr.year_month,
                wins=mr.wins,
                improvements=mr.improvements,
                notes=mr.notes
            )
            new_session.add(new_mr)
        new_session.commit()
        
        print("Migration completed successfully!")
    
    except Exception as e:
        print(f"Migration failed: {e}")
        new_session.rollback()
        # Restore old db
        new_session.close()
        new_engine.dispose()
        old_session.close()
        old_engine.dispose()
        os.remove(old_db_path)
        shutil.copy2(backup_db_path, old_db_path)
        print("Restored original database.")
    finally:
        try:
            old_session.close()
            new_session.close()
        except:
            pass

if __name__ == "__main__":
    migrate()
