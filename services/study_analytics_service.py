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
    # 0.15 hours
    last_7 = db.query(func.sum(StudySession.duration_minutes))\
               .filter(StudySession.status == 'completed', StudySession.completion_date > today - timedelta(days=7), StudySession.completion_date <= today).scalar() or 0
    prev_7 = db.query(func.sum(StudySession.duration_minutes))\
               .filter(StudySession.status == 'completed', StudySession.completion_date > today - timedelta(days=14), StudySession.completion_date <= today - timedelta(days=7)).scalar() or 0
    
    hours_factor = 0
    if prev_7 > 0 and last_7 < prev_7:
        hours_factor = (prev_7 - last_7) / prev_7
        
    # 0.35 sleep
    sleep_avg = db.query(func.avg(DailyJournal.sleep_hours))\
                  .filter(DailyJournal.date > today - timedelta(days=3), DailyJournal.date <= today).scalar() or 7.0
    sleep_factor = max(0, (7.0 - sleep_avg) / 7.0)
    
    # 0.20 mood
    negative_moods = ["😔 Sad", "😠 Frustrated", "😴 Tired"]
    recent_journals = db.query(DailyJournal)\
                        .filter(DailyJournal.date > today - timedelta(days=5), DailyJournal.date <= today).all()
    moods = [j.mood for j in recent_journals if j.mood]
    mood_factor = sum(1 for m in moods if m in negative_moods) / 5.0
    
    # 0.30 stress
    stress_avg = db.query(func.avg(DailyJournal.stress_score))\
                  .filter(DailyJournal.date > today - timedelta(days=5), DailyJournal.date <= today).scalar() or 0.0
    stress_factor = stress_avg / 10.0
    
    burnout_score = (0.35 * sleep_factor) + (0.30 * stress_factor) + (0.20 * mood_factor) + (0.15 * hours_factor)
    
    is_burnout = burnout_score > 0.6
    
    return {
        "is_burnout": is_burnout,
        "burnout_score": round(burnout_score, 2),
        "hours_drop": hours_factor > 0.5,
        "low_sleep": sleep_factor > 0.5,
        "negative_streak": mood_factor > 0.5
    }

def get_most_productive_weekday(db: Session):
    sessions = db.query(
        func.strftime('%w', StudySession.completion_date).label('weekday'),
        func.sum(StudySession.duration_minutes).label('total')
    ).filter(StudySession.status == 'completed').group_by('weekday').all()
    
    if not sessions:
        return "N/A"
    best = max(sessions, key=lambda x: x.total)
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if best.weekday is not None:
        return days[int(best.weekday)]
    return "N/A"

def get_best_study_hour(db: Session):
    sessions = db.query(
        func.strftime('%H', StudySession.actual_start).label('hour'),
        func.sum(StudySession.duration_minutes).label('total')
    ).filter(StudySession.status == 'completed', StudySession.actual_start != None).group_by('hour').all()
    
    if not sessions:
        return "N/A"
    best = max(sessions, key=lambda x: x.total)
    if best.hour is not None:
        return f"{best.hour}:00"
    return "N/A"

def get_most_neglected_subject(db: Session):
    # Subject with least hours completed but highest priority / estimated hours
    subjects = get_subject_progress(db)
    if subjects.empty:
        return "N/A"
    
    # Sort by lowest progress
    subjects = subjects.sort_values(by="Progress %", ascending=True)
    return subjects.iloc[0]["Subject"]

def get_study_consistency_score(db: Session, today: date):
    start_date = today - timedelta(days=13)
    completed_sessions = db.query(StudySession.completion_date)\
                           .filter(StudySession.status == 'completed', 
                                   StudySession.completion_date >= start_date, 
                                   StudySession.completion_date <= today).all()
    unique_days = len(set([s[0] for s in completed_sessions if s[0]]))
    score = int((unique_days / 14) * 100)
    return unique_days, score
