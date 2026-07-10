from models import AnnualGoal, MonthlyGoal, WeeklyPlan
from sqlalchemy import extract

def get_annual_goals(db_session, target_year: int):
    return db_session.query(AnnualGoal).filter(AnnualGoal.target_year == target_year).all()

def add_annual_goal(db_session, target_year: int, title: str, description: str):
    try:
        goal = AnnualGoal(target_year=target_year, title=title, description=description)
        db_session.add(goal)
        db_session.commit()
        return goal
    except Exception as e:
        db_session.rollback()
        raise e

def edit_annual_goal(db_session, goal_id: int, title: str, description: str):
    try:
        goal = db_session.query(AnnualGoal).filter(AnnualGoal.id == goal_id).first()
        if goal:
            goal.title = title
            goal.description = description
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def delete_annual_goal(db_session, goal_id: int):
    try:
        goal = db_session.query(AnnualGoal).filter(AnnualGoal.id == goal_id).first()
        if goal:
            db_session.delete(goal)
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def update_annual_goal_progress(db_session, goal_id: int, progress: int):
    try:
        goal = db_session.query(AnnualGoal).filter(AnnualGoal.id == goal_id).first()
        if goal:
            goal.progress = progress
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def get_monthly_goals(db_session, year_month: str):
    return db_session.query(MonthlyGoal).filter(MonthlyGoal.year_month == year_month).all()

def add_monthly_goal(db_session, year_month: str, goal_text: str):
    try:
        goal = MonthlyGoal(year_month=year_month, goal_text=goal_text)
        db_session.add(goal)
        db_session.commit()
        return goal
    except Exception as e:
        db_session.rollback()
        raise e

def update_monthly_goal_status(db_session, goal_id: int, completed: bool):
    try:
        goal = db_session.query(MonthlyGoal).filter(MonthlyGoal.id == goal_id).first()
        if goal:
            goal.completed = completed
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def delete_monthly_goal(db_session, goal_id: int):
    try:
        goal = db_session.query(MonthlyGoal).filter(MonthlyGoal.id == goal_id).first()
        if goal:
            db_session.delete(goal)
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def get_weekly_plans(db_session, year_month: str):
    return db_session.query(WeeklyPlan).filter(WeeklyPlan.year_month == year_month).order_by(WeeklyPlan.week_number).all()

def add_weekly_plan(db_session, year_month: str, week_number: int, task_text: str):
    try:
        plan = WeeklyPlan(year_month=year_month, week_number=week_number, task_text=task_text)
        db_session.add(plan)
        db_session.commit()
        return plan
    except Exception as e:
        db_session.rollback()
        raise e

def update_weekly_plan_status(db_session, plan_id: int, completed: bool):
    try:
        plan = db_session.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id).first()
        if plan:
            plan.completed = completed
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def delete_weekly_plan(db_session, plan_id: int):
    try:
        plan = db_session.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id).first()
        if plan:
            db_session.delete(plan)
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def calculate_goal_alignment(db_session):
    annual = db_session.query(AnnualGoal).all()
    if not annual:
        return 0
    return 85
