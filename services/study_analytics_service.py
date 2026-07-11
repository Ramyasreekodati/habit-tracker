import pandas as pd
from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy import func
from models import StudySession, Subject, RevisionQueue, DailyJournal

def get_study_hours_by_subject(db: Session, start_date: date, end_date: date):
    # Total hours per subject
    sessions = db.query(
        Subject.name,
        func.sum(StudySession.duration_minutes).label('total_minutes')
    ).join(StudySession, Subject.id == StudySession.subject_id)\
     .filter(StudySession.status == 'completed')\
     .filter(StudySession.completion_date >= start_date)\
     .filter(StudySession.completion_date <= end_date)\
     .group_by(Subject.name).all()
     
    data = [{"Subject": s.name, "Hours": round(s.total_minutes / 60, 1)} for s in sessions if s.total_minutes]
    return pd.DataFrame(data)

def get_subject_progress(db: Session):
    subjects = db.query(Subject).filter(Subject.active == True).all()
    data = []
    for sub in subjects:
        total_mins = db.query(func.sum(StudySession.duration_minutes))\
                       .filter(StudySession.subject_id == sub.id, StudySession.status == 'completed').scalar() or 0
        comp_hours = total_mins / 60
        est_hours = sub.estimated_total_hours if sub.estimated_total_hours > 0 else 1
        progress = (comp_hours / est_hours) * 100
        data.append({
            "Subject": sub.name,
            "Completed Hours": round(comp_hours, 1),
            "Target Hours": est_hours,
            "Progress %": min(round(progress, 1), 100)
        })
    return pd.DataFrame(data)

def get_deep_work_hours(db: Session, start_date: date, end_date: date):
    # Sessions >= 50 mins
    total_mins = db.query(func.sum(StudySession.duration_minutes))\
                   .filter(StudySession.status == 'completed', StudySession.duration_minutes >= 50)\
                   .filter(StudySession.completion_date >= start_date)\
                   .filter(StudySession.completion_date <= end_date).scalar() or 0
    return round(total_mins / 60, 1)

def get_revision_completion_rate(db: Session, start_date: date, end_date: date):
    total = db.query(RevisionQueue).filter(
        RevisionQueue.revision_date >= start_date,
        RevisionQueue.revision_date <= end_date
    ).count()
    if total == 0:
        return 0
    completed = db.query(RevisionQueue).filter(
        RevisionQueue.revision_date >= start_date,
        RevisionQueue.revision_date <= end_date,
        RevisionQueue.completed == True
    ).count()
    return round((completed / total) * 100, 1)

def check_burnout_warning(db: Session, today: date):
    # Rule 1: Study hours down 40% (comparing last 7 days vs previous 7 days)
    last_7 = db.query(func.sum(StudySession.duration_minutes))\
               .filter(StudySession.status == 'completed', StudySession.completion_date > today - timedelta(days=7), StudySession.completion_date <= today).scalar() or 0
    prev_7 = db.query(func.sum(StudySession.duration_minutes))\
               .filter(StudySession.status == 'completed', StudySession.completion_date > today - timedelta(days=14), StudySession.completion_date <= today - timedelta(days=7)).scalar() or 0
    
    hours_drop = False
    if prev_7 > 0 and (last_7 / prev_7) <= 0.6:
        hours_drop = True
        
    # Rule 2: average sleep < 6h over last 3 days
    sleep_avg = db.query(func.avg(DailyJournal.sleep_hours))\
                  .filter(DailyJournal.date > today - timedelta(days=3), DailyJournal.date <= today).scalar() or 7.0
    low_sleep = sleep_avg < 6.0
    
    # Rule 3: mood negative for 5 days
    negative_moods = ["😔 Sad", "😠 Frustrated", "😴 Tired"]
    recent_journals = db.query(DailyJournal.mood)\
                        .filter(DailyJournal.date > today - timedelta(days=5), DailyJournal.date <= today).all()
    moods = [j.mood for j in recent_journals if j.mood]
    negative_streak = len(moods) == 5 and all(m in negative_moods for m in moods)
    
    is_burnout = hours_drop and low_sleep and negative_streak
    
    return {
        "is_burnout": is_burnout,
        "hours_drop": hours_drop,
        "low_sleep": low_sleep,
        "negative_streak": negative_streak
    }
