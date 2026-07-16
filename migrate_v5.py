import sqlite3
from database import engine, Base
import models # ensure models are registered

def migrate():
    engine.dispose()
    
    conn = sqlite3.connect('growthos.db')
    cursor = conn.cursor()
    
    tables = [
        "monthly_goals", "study_sessions", "subject_dependencies"
    ]
    
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
    
    Base.metadata.create_all(engine)
    
    conn = sqlite3.connect('growthos.db')
    cursor = conn.cursor()
    
    try:
        # 1. monthly_goals
        cursor.execute("INSERT INTO monthly_goals (id, year_month, goal_text, completed, progress_mode, progress, weight, annual_goal_id, created_at, updated_at) SELECT id, year_month, goal_text, completed, 'manual', CASE WHEN completed THEN 100 ELSE 0 END, 1, annual_goal_id, created_at, updated_at FROM old_monthly_goals")
        print("Copied monthly_goals")
    except sqlite3.OperationalError as e:
        print("Error monthly_goals:", e)

    try:
        # 2. subject_dependencies
        cursor.execute("INSERT INTO subject_dependencies (subject_id, depends_on_id, is_required) SELECT subject_id, depends_on_id, 1 FROM old_subject_dependencies")
        print("Copied subject_dependencies")
    except sqlite3.OperationalError as e:
        print("Error subject_dependencies:", e)

    try:
        # 3. study_sessions
        cursor.execute("SELECT id, planned_date, completion_date, subject_id, topic, duration_minutes, status, energy_level, difficulty, notes, planned_start, planned_end, actual_start, actual_end, session_type, source_type, resource_name, priority, monthly_goal_id, weekly_plan_id, created_at FROM old_study_sessions")
        rows = cursor.fetchall()
        for r in rows:
            pri_map = {"High": 3, "Medium": 2, "Low": 1}
            p_val = pri_map.get(r[17], 2) if isinstance(r[17], str) else (r[17] if r[17] in [1,2,3] else 2)
            
            cursor.execute("INSERT INTO study_sessions (id, planned_date, completion_date, subject_id, topic, duration_minutes, status, energy_level, difficulty, notes, planned_start, planned_end, actual_start, actual_end, session_type, source_type, resource_name, resource_url, priority, monthly_goal_id, weekly_plan_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?, ?, ?)", (*r[:17], p_val, *r[18:]))
        print("Copied study_sessions")
    except sqlite3.OperationalError as e:
        print("Error study_sessions:", e)

    for table in tables:
        try:
            cursor.execute(f"DROP TABLE old_{table}")
        except sqlite3.OperationalError:
            pass
            
    conn.commit()
    
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
    
    print("Migration to v5 complete!")

if __name__ == "__main__":
    migrate()
