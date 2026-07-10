import sqlite3
from database import engine, Base
import models # ensure models are registered

def migrate():
    # 1. Close active engine connections
    engine.dispose()
    
    # 2. Connect via sqlite3 to rename tables
    conn = sqlite3.connect('growthos.db')
    cursor = conn.cursor()
    
    tables = [
        "habits", "habit_logs", "annual_goals", "monthly_goals", 
        "weekly_plans", "monthly_reflections", "daily_journals", "weekly_reviews"
    ]
    
    # Drop all non-internal indexes so create_all can recreate them for new tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    indexes = cursor.fetchall()
    for (idx_name,) in indexes:
        try:
            cursor.execute(f"DROP INDEX {idx_name}")
        except sqlite3.OperationalError:
            pass

    
    for table in tables:
        try:
            cursor.execute(f"ALTER TABLE {table} RENAME TO old_{table}")
        except sqlite3.OperationalError:
            print(f"Could not rename {table} (might not exist or already renamed)")
            
    conn.commit()
    conn.close()
    
    # 3. Recreate tables with new schema
    Base.metadata.create_all(engine)
    
    # 4. Copy data
    conn = sqlite3.connect('growthos.db')
    cursor = conn.cursor()
    
    copy_queries = {
        "habits": "INSERT INTO habits (id, name, category, monthly_goal, reward, frequency_type, created_at, is_active, display_order, difficulty, notes) SELECT id, name, category, monthly_goal, reward, frequency_type, created_at, is_active, display_order, difficulty, notes FROM old_habits",
        "habit_logs": "INSERT INTO habit_logs (id, habit_id, log_date, status, note, missed_reason) SELECT id, habit_id, log_date, status, note, missed_reason FROM old_habit_logs",
        "annual_goals": "INSERT INTO annual_goals (id, target_year, title, description, progress) SELECT id, target_year, title, description, progress FROM old_annual_goals",
        "monthly_goals": "INSERT INTO monthly_goals (id, year_month, goal_text, completed) SELECT id, year_month, goal_text, completed FROM old_monthly_goals",
        "weekly_plans": "INSERT INTO weekly_plans (id, year_month, week_number, task_text, completed) SELECT id, year_month, week_number, task_text, completed FROM old_weekly_plans",
        "monthly_reflections": "INSERT INTO monthly_reflections (id, year_month, wins, improvements, notes) SELECT id, year_month, wins, improvements, notes FROM old_monthly_reflections",
        "daily_journals": "INSERT INTO daily_journals (id, date, mood, energy, sleep_hours, focus_score, stress_score, notes) SELECT id, date, mood, energy, sleep_hours, focus_score, stress_score, notes FROM old_daily_journals",
        "weekly_reviews": "INSERT INTO weekly_reviews (id, week_start, wins, failures, distractions, next_week_priority) SELECT id, week_start, wins, failures, distractions, next_week_priority FROM old_weekly_reviews"
    }
    
    for table, query in copy_queries.items():
        try:
            cursor.execute(query)
            print(f"Copied data for {table}")
        except sqlite3.OperationalError as e:
            print(f"Error copying {table}: {e}")
            
    # 5. Drop old tables
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE old_{table}")
        except sqlite3.OperationalError:
            pass
            
    conn.commit()
    conn.close()
    
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
