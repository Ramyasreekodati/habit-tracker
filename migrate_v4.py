import sqlite3
from database import engine, Base
import models # ensure models are registered

def migrate():
    # 1. Close active engine connections
    engine.dispose()
    
    conn = sqlite3.connect('growthos.db')
    cursor = conn.cursor()
    
    tables = [
        "monthly_goals", "weekly_plans", "study_sessions"
    ]
    
    # Store counts for validation
    counts_before = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts_before[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            counts_before[table] = 0
            
    # Drop indexes
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
        "monthly_goals": "INSERT INTO monthly_goals (id, year_month, goal_text, completed, annual_goal_id, created_at, updated_at) SELECT id, year_month, goal_text, completed, NULL, created_at, updated_at FROM old_monthly_goals",
        "weekly_plans": "INSERT INTO weekly_plans (id, year_month, week_number, task_text, completed, monthly_goal_id, created_at, updated_at) SELECT id, year_month, week_number, task_text, completed, NULL, created_at, updated_at FROM old_weekly_plans",
        "study_sessions": "INSERT INTO study_sessions (id, planned_date, completion_date, subject_id, topic, duration_minutes, status, energy_level, difficulty, notes, planned_start, planned_end, actual_start, actual_end, session_type, source_type, resource_name, priority, monthly_goal_id, weekly_plan_id, created_at) SELECT id, planned_date, completion_date, subject_id, topic, duration_minutes, status, energy_level, difficulty, notes, planned_start, planned_end, actual_start, actual_end, session_type, source_type, '', 'Medium', monthly_goal_id, weekly_plan_id, created_at FROM old_study_sessions"
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
    
    # 6. Validate Integrity
    counts_after = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts_after[table] = cursor.fetchone()[0]
        
    for table in tables:
        if counts_before[table] == counts_after[table]:
            print(f"PASS: {table} count ({counts_before[table]} == {counts_after[table]})")
        else:
            print(f"FAIL: {table} count mismatch ({counts_before[table]} != {counts_after[table]})")

    conn.close()
    
    print("Migration to v4 complete!")

if __name__ == "__main__":
    migrate()
