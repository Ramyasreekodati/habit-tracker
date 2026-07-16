from models import Subject, StudySession, RevisionQueue
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

# --- Subject Service ---

def get_subjects(db: Session, active_only: bool = True):
    query = db.query(Subject)
    if active_only:
        query = query.filter(Subject.active == True)
    return query.all()

def add_subject(db: Session, name: str, category: str, priority: int, estimated_total_hours: int, color: str, required_deps: list[int] = None, optional_deps: list[int] = None):
    from sqlalchemy.exc import IntegrityError
    from models import SubjectDependency
    
    subject = Subject(
        name=name,
        category=category,
        priority=priority,
        estimated_total_hours=estimated_total_hours,
        color=color
    )
    
    if required_deps:
        for dep_id in required_deps:
            subject.dependency_links.append(SubjectDependency(depends_on_id=dep_id, is_required=True))
            
    if optional_deps:
        for dep_id in optional_deps:
            subject.dependency_links.append(SubjectDependency(depends_on_id=dep_id, is_required=False))

    db.add(subject)
    try:
        db.commit()
        db.refresh(subject)
        return subject
    except IntegrityError:
        db.rollback()
        return None

def mark_subject_completed(db: Session, subject_id: int, completed: bool = True):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject:
        subject.is_completed = completed
        db.commit()
    return subject

# --- Study Session Service ---

def get_study_sessions(db: Session, start_date: date = None, end_date: date = None):
    query = db.query(StudySession)
    if start_date:
        query = query.filter(StudySession.planned_date >= start_date)
    if end_date:
        query = query.filter(StudySession.planned_date <= end_date)
    return query.order_by(StudySession.planned_date.desc()).all()

def add_study_session(db: Session, planned_date: date, subject_id: int, topic: str, duration_minutes: int, 
                      session_type: str, source_type: str, monthly_goal_id: int = None, weekly_plan_id: int = None,
                      priority: int = 2, resource_name: str = "", resource_url: str = ""):
    session = StudySession(
        planned_date=planned_date,
        subject_id=subject_id,
        topic=topic,
        duration_minutes=duration_minutes,
        session_type=session_type,
        source_type=source_type,
        monthly_goal_id=monthly_goal_id,
        weekly_plan_id=weekly_plan_id,
        priority=priority,
        resource_name=resource_name,
        resource_url=resource_url
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def update_session_status(db: Session, session_id: int, status: str, 
                          actual_start: datetime = None, actual_end: datetime = None, 
                          completion_date: date = None, difficulty: int = 5, energy_level: int = 5, notes: str = ""):
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if session:
        session.status = status
        if status == 'completed':
            session.actual_start = actual_start
            session.actual_end = actual_end
            session.completion_date = completion_date or date.today()
            session.difficulty = difficulty
            session.energy_level = energy_level
            session.notes = notes
            
            # Generate Revision Queue if Learning session
            if session.session_type == 'Learning':
                generate_revisions(db, session.id, session.completion_date)
                
        db.commit()
    return session

def delete_study_session(db: Session, session_id: int):
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()

def edit_study_session(db: Session, session_id: int, topic: str, duration_minutes: int, 
                       session_type: str, source_type: str, monthly_goal_id: int = None, weekly_plan_id: int = None,
                       priority: int = 2, resource_name: str = "", resource_url: str = ""):
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if session:
        session.topic = topic
        session.duration_minutes = duration_minutes
        session.session_type = session_type
        session.source_type = source_type
        session.monthly_goal_id = monthly_goal_id
        session.weekly_plan_id = weekly_plan_id
        session.priority = priority
        session.resource_name = resource_name
        session.resource_url = resource_url
        db.commit()
    return session

# --- Revision Engine Service ---

def generate_revisions(db: Session, learning_session_id: int, completion_date: date):
    # R1: +1, R2: +3, R3: +7, R4: +21, R5: +45
    offsets = [1, 3, 7, 21, 45]
    for stage, offset in enumerate(offsets, start=1):
        rev_date = completion_date + timedelta(days=offset)
        rev = RevisionQueue(
            learning_session_id=learning_session_id,
            revision_date=rev_date,
            revision_stage=stage
        )
        db.add(rev)
    # Don't commit here, it's committed by the caller (update_session_status)
