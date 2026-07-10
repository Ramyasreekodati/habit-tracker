import pandas as pd
from datetime import date
import calendar
from models import Habit, HabitLog
from services.analytics_service import get_habit_logs_df

def generate_monthly_report(db_session, year: int, month: int):
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    
    df_logs = get_habit_logs_df(db_session, start_date, end_date)
    habits = db_session.query(Habit).filter(Habit.is_active == True).all()
    
    report = {
        "Month": start_date.strftime('%B %Y'),
        "Total Habits Tracked": len(habits),
        "Total Completions": 0,
        "Success Rate": 0.0,
        "Best Habit": "N/A",
        "Weakest Habit": "N/A",
        "Productivity Score": 0,
        "Top Missed Reason": "N/A"
    }
    
    if df_logs.empty:
        return report
        
    completed = df_logs[df_logs['status'] == 'completed']
    report["Total Completions"] = len(completed)
    
    # Best & Weakest Habit
    if not completed.empty:
        habit_counts = completed['habit_id'].value_counts()
        best_id = habit_counts.idxmax()
        worst_id = habit_counts.idxmin()
        best_h = next((h for h in habits if h.id == best_id), None)
        worst_h = next((h for h in habits if h.id == worst_id), None)
        
        report["Best Habit"] = best_h.name if best_h else "N/A"
        report["Weakest Habit"] = worst_h.name if worst_h else "N/A"
        
        # Success Rate
        total_available = len(habits) * end_date.day # rough estimate for the month up to current day if current month
        if year == date.today().year and month == date.today().month:
            total_available = len(habits) * date.today().day
        
        if total_available > 0:
            report["Success Rate"] = round((len(completed) / total_available) * 100, 1)
            report["Productivity Score"] = int(report["Success Rate"])
            
    # Missed reasons
    missed = df_logs[(df_logs['status'] == 'missed') & (df_logs['missed_reason'] != "")]
    if not missed.empty:
        report["Top Missed Reason"] = missed['missed_reason'].value_counts().idxmax()
        
    return report

def generate_csv_report(db_session, year: int, month: int):
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    df_logs = get_habit_logs_df(db_session, start_date, end_date)
    return df_logs.to_csv(index=False)
