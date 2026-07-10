import argparse
import random
from datetime import date, timedelta, datetime
from database import SessionLocal, Base, engine
from models import Habit, HabitLog, DailyJournal, AnnualGoal, MonthlyGoal, WeeklyPlan

# Profiles Definition
PROFILES = {
    "student": {
        "annual_goal": "Graduate with Honors",
        "habits": [
            {"name": "Study Core Subjects", "category": "Learning", "goal": 20, "diff": 3, "freq": 0.8},
            {"name": "Revision Notes", "category": "Learning", "goal": 15, "diff": 2, "freq": 0.6},
            {"name": "Read 10 Pages", "category": "Learning", "goal": 25, "diff": 1, "freq": 0.9},
            {"name": "Exercise", "category": "Health", "goal": 12, "diff": 2, "freq": 0.4}
        ]
    },
    "developer": {
        "annual_goal": "Land a Senior SWE Role",
        "habits": [
            {"name": "LeetCode (1 Problem)", "category": "Career", "goal": 25, "diff": 3, "freq": 0.8},
            {"name": "System Design Study", "category": "Career", "goal": 10, "diff": 3, "freq": 0.4},
            {"name": "Open Source Commits", "category": "Career", "goal": 15, "diff": 2, "freq": 0.5},
            {"name": "Deep Work (2 Hrs)", "category": "Productivity", "goal": 20, "diff": 3, "freq": 0.7} # Drops on weekends
        ]
    },
    "fitness": {
        "annual_goal": "Run a Marathon & Stay Lean",
        "habits": [
            {"name": "Morning Run", "category": "Health", "goal": 20, "diff": 3, "freq": 0.7},
            {"name": "Drink 3L Water", "category": "Health", "goal": 30, "diff": 1, "freq": 0.95},
            {"name": "Gym / Strength", "category": "Health", "goal": 12, "diff": 3, "freq": 0.4},
            {"name": "Sleep 8 Hours", "category": "Health", "goal": 25, "diff": 2, "freq": 0.8}
        ]
    },
    "entrepreneur": {
        "annual_goal": "Hit $10k MRR",
        "habits": [
            {"name": "Sales Outreach (20 DMs)", "category": "Career", "goal": 22, "diff": 3, "freq": 0.75},
            {"name": "Content Creation", "category": "Career", "goal": 15, "diff": 2, "freq": 0.5},
            {"name": "Deep Work (90 mins)", "category": "Productivity", "goal": 25, "diff": 3, "freq": 0.8},
            {"name": "Network (1 Call)", "category": "Career", "goal": 10, "diff": 2, "freq": 0.3}
        ]
    }
}

def clear_db(db):
    print("Clearing database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_profile(profile_name: str, days: int = 60):
    if profile_name not in PROFILES:
        print(f"Error: Profile '{profile_name}' not found. Choose from {list(PROFILES.keys())}")
        return

    db = SessionLocal()
    clear_db(db)
    
    print(f"Seeding profile: {profile_name.capitalize()}")
    data = PROFILES[profile_name]
    today = date.today()
    start_date = today - timedelta(days=days)
    
    # 1. Goals
    ag = AnnualGoal(target_year=today.year, title=data["annual_goal"], description="Auto-seeded goal", progress=45)
    db.add(ag)
    
    ym = f"{today.year}-{today.month:02d}"
    db.add(MonthlyGoal(year_month=ym, goal_text="Make significant progress", completed=False))
    db.add(WeeklyPlan(year_month=ym, week_number=1, task_text="Start strong", completed=True))
    db.add(WeeklyPlan(year_month=ym, week_number=2, task_text="Keep momentum", completed=False))
    
    # 2. Habits
    created_habits = []
    for h in data["habits"]:
        habit = Habit(
            name=h["name"],
            category=h["category"],
            monthly_goal=h["goal"],
            reward="Treat Yourself",
            difficulty=h["diff"],
            created_at=datetime.combine(start_date, datetime.min.time())
        )
        db.add(habit)
        created_habits.append((habit, h["freq"]))
    db.commit()

    # 3. Logs & Journals (Generate realistic data)
    print(f"Generating {days} days of mock history...")
    
    current_date = start_date
    while current_date <= today:
        is_weekend = current_date.weekday() >= 5
        
        # Daily Journal
        moods = ["😊 Happy", "😌 Calm", "😐 Neutral", "😔 Sad", "😴 Tired"]
        journal = DailyJournal(
            date=current_date,
            mood=random.choice(moods),
            energy=random.randint(4, 9) if not is_weekend else random.randint(6, 10),
            sleep_hours=random.randint(5, 9),
            focus_score=random.randint(4, 10) if not is_weekend else random.randint(2, 7),
            stress_score=random.randint(2, 8)
        )
        db.add(journal)
        
        # Habit Logs
        for habit, freq in created_habits:
            # Adjust frequency based on profile logic (e.g., developers code less on weekends)
            adjusted_freq = freq
            if profile_name == "developer" and is_weekend and habit.category == "Career":
                adjusted_freq *= 0.3 
                
            status = ""
            missed_reason = ""
            
            if random.random() < adjusted_freq:
                status = "completed"
            else:
                status = "missed"
                if random.random() < 0.4:
                    missed_reason = random.choice(["Busy", "Sick", "Forgot", "Travel", "Low Motivation"])
                    
            log = HabitLog(
                habit_id=habit.id,
                log_date=current_date,
                status=status,
                missed_reason=missed_reason
            )
            db.add(log)
            
        current_date += timedelta(days=1)

    db.commit()
    db.close()
    print("Seed complete! Run the app to see the populated dashboard.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed GrowthOS database with a realistic profile.")
    parser.add_argument("--profile", type=str, choices=PROFILES.keys(), required=True, help="Profile type to generate.")
    parser.add_argument("--days", type=int, default=90, help="Number of days of history to generate.")
    args = parser.parse_args()
    
    seed_profile(args.profile, args.days)
