from models import AnnualGoal, MonthlyGoal, WeeklyPlan
from sqlalchemy import extract

def get_annual_goals(db_session, target_year: int):
    return db_session.query(AnnualGoal).filter(AnnualGoal.target_year == target_year).all()

def add_annual_goal(db_session, target_year: int, title: str, description: str):
    goal = AnnualGoal(target_year=target_year, title=title, description=description)
    db_session.add(goal)
    db_session.commit()
    return goal

def update_annual_goal_progress(db_session, goal_id: int, progress: int):
    goal = db_session.query(AnnualGoal).filter(AnnualGoal.id == goal_id).first()
    if goal:
        goal.progress = progress
        db_session.commit()

def get_monthly_goals(db_session, year_month: str):
    return db_session.query(MonthlyGoal).filter(MonthlyGoal.year_month == year_month).all()

def add_monthly_goal(db_session, year_month: str, goal_text: str):
    goal = MonthlyGoal(year_month=year_month, goal_text=goal_text)
    db_session.add(goal)
    db_session.commit()
    return goal

def get_weekly_plans(db_session, year_month: str):
    return db_session.query(WeeklyPlan).filter(WeeklyPlan.year_month == year_month).order_by(WeeklyPlan.week_number).all()

def add_weekly_plan(db_session, year_month: str, week_number: int, task_text: str):
    plan = WeeklyPlan(year_month=year_month, week_number=week_number, task_text=task_text)
    db_session.add(plan)
    db_session.commit()
    return plan

def calculate_goal_alignment(db_session):
    # Dummy logic to calculate goal alignment based on active habits vs annual goals
    # In a real app this might use tag matching or NLP. 
    # For now, it returns a static high score to demonstrate the feature.
    annual = db_session.query(AnnualGoal).all()
    if not annual:
        return 0
    # Base alignment score on overall average completion vs goal progress
    return 85 # 85% alignment score dummy
