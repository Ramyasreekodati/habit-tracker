from models import DailyJournal, WeeklyReview, MonthlyReflection
from datetime import date, timedelta

def get_daily_journal(db_session, target_date: date):
    journal = db_session.query(DailyJournal).filter(DailyJournal.date == target_date).first()
    if not journal:
        journal = DailyJournal(date=target_date)
    return journal

def save_daily_journal(db_session, target_date: date, mood: str, energy: int, sleep: int, focus: int, stress: int, notes: str):
    journal = db_session.query(DailyJournal).filter(DailyJournal.date == target_date).first()
    if not journal:
        journal = DailyJournal(date=target_date)
        db_session.add(journal)
    
    journal.mood = mood
    journal.energy = energy
    journal.sleep_hours = sleep
    journal.focus_score = focus
    journal.stress_score = stress
    journal.notes = notes
    
    db_session.commit()
    return journal

def get_weekly_review(db_session, target_date: date):
    # Get the Monday of the current week
    week_start = target_date - timedelta(days=target_date.weekday())
    review = db_session.query(WeeklyReview).filter(WeeklyReview.week_start == week_start).first()
    if not review:
        review = WeeklyReview(week_start=week_start)
    return review

def save_weekly_review(db_session, target_date: date, wins: str, failures: str, distractions: str, priority: str):
    week_start = target_date - timedelta(days=target_date.weekday())
    review = db_session.query(WeeklyReview).filter(WeeklyReview.week_start == week_start).first()
    if not review:
        review = WeeklyReview(week_start=week_start)
        db_session.add(review)
    
    review.wins = wins
    review.failures = failures
    review.distractions = distractions
    review.next_week_priority = priority
    
    db_session.commit()
    return review

def get_monthly_reflection(db_session, year: int, month: int):
    ym = f"{year}-{month:02d}"
    reflection = db_session.query(MonthlyReflection).filter(MonthlyReflection.year_month == ym).first()
    if not reflection:
        reflection = MonthlyReflection(year_month=ym)
    return reflection

def save_monthly_reflection(db_session, year: int, month: int, wins: str, improvements: str, notes: str):
    ym = f"{year}-{month:02d}"
    reflection = db_session.query(MonthlyReflection).filter(MonthlyReflection.year_month == ym).first()
    if not reflection:
        reflection = MonthlyReflection(year_month=ym)
        db_session.add(reflection)
        
    reflection.wins = wins
    reflection.improvements = improvements
    reflection.notes = notes
    
    db_session.commit()
    return reflection
