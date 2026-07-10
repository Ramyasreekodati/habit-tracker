import pandas as pd
from datetime import date, timedelta
import calendar
from models import Habit, HabitLog

def get_habit_logs_df(db_session, start_date=None, end_date=None):
    query = db_session.query(HabitLog)
    if start_date:
        query = query.filter(HabitLog.log_date >= start_date)
    if end_date:
        query = query.filter(HabitLog.log_date <= end_date)
    
    logs = query.all()
    if not logs:
        return pd.DataFrame()
        
    df = pd.DataFrame([{
        "habit_id": l.habit_id, 
        "log_date": pd.to_datetime(l.log_date), 
        "status": l.status,
        "missed_reason": l.missed_reason
    } for l in logs])
    return df

def generate_heatmap_data(df_logs):
    if df_logs.empty:
        return pd.DataFrame()
        
    # Group by date and count completions
    completed = df_logs[df_logs['status'] == 'completed']
    daily_counts = completed.groupby('log_date').size().reset_index(name='completions')
    
    # Ensure all dates in range are present
    if not daily_counts.empty:
        start = daily_counts['log_date'].min()
        end = daily_counts['log_date'].max()
        all_dates = pd.date_range(start, end)
        daily_counts = daily_counts.set_index('log_date').reindex(all_dates).fillna(0).reset_index()
        daily_counts.rename(columns={'index': 'log_date'}, inplace=True)
        
        # Add week and weekday for heatmap layout
        daily_counts['week'] = daily_counts['log_date'].dt.isocalendar().week
        daily_counts['weekday'] = daily_counts['log_date'].dt.weekday # 0=Mon, 6=Sun
    return daily_counts

def calculate_success_rates(db_session):
    habits = db_session.query(Habit).filter(Habit.is_active == True).all()
    df_logs = get_habit_logs_df(db_session)
    
    results = []
    today = date.today()
    for h in habits:
        h_created = h.created_at.date()
        available_days = (today - h_created).days + 1
        if available_days <= 0:
            continue
            
        if not df_logs.empty:
            h_logs = df_logs[df_logs['habit_id'] == h.id]
            completed_days = len(h_logs[h_logs['status'] == 'completed'])
        else:
            completed_days = 0
            
        rate = (completed_days / available_days) * 100
        results.append({
            "Habit": h.name,
            "Category": h.category,
            "Available Days": available_days,
            "Completed": completed_days,
            "Success Rate (%)": round(rate, 1)
        })
    return pd.DataFrame(results)

def calculate_forecasting(db_session, year, month):
    habits = db_session.query(Habit).filter(Habit.is_active == True).all()
    num_days_in_month = calendar.monthrange(year, month)[1]
    today = date.today()
    
    # Only forecast if we are in the current month
    if year != today.year or month != today.month:
        return pd.DataFrame()
        
    start_date = date(year, month, 1)
    df_logs = get_habit_logs_df(db_session, start_date=start_date)
    
    results = []
    days_passed = today.day
    days_remaining = num_days_in_month - days_passed
    
    for h in habits:
        if not df_logs.empty:
            h_logs = df_logs[df_logs['habit_id'] == h.id]
            completed_so_far = len(h_logs[h_logs['status'] == 'completed'])
        else:
            completed_so_far = 0
            
        goal = h.monthly_goal
        
        # Simple projection: daily completion rate so far * total days
        current_rate = completed_so_far / days_passed if days_passed > 0 else 0
        projected = int(completed_so_far + (current_rate * days_remaining))
        
        # Probability based on required rate vs current rate
        if projected >= goal:
            prob = 99
        else:
            required_remaining = goal - completed_so_far
            if required_remaining > days_remaining:
                prob = 0
            else:
                prob = int((projected / goal) * 100) if goal > 0 else 100
                
        results.append({
            "Habit": h.name,
            "Goal": goal,
            "Current Pace": completed_so_far,
            "Projected": min(projected, num_days_in_month),
            "Probability (%)": min(prob, 100)
        })
    return pd.DataFrame(results)

def calculate_recovery_metrics(db_session):
    # Calculates average days taken to recover after a missed day
    df_logs = get_habit_logs_df(db_session)
    if df_logs.empty:
        return 0.0
        
    df_logs = df_logs.sort_values(by=['habit_id', 'log_date'])
    recovery_times = []
    
    for habit_id, group in df_logs.groupby('habit_id'):
        missed_streak = 0
        for _, row in group.iterrows():
            if row['status'] == 'missed':
                missed_streak += 1
            elif row['status'] == 'completed':
                if missed_streak > 0:
                    recovery_times.append(missed_streak)
                    missed_streak = 0
                    
    if recovery_times:
        return round(sum(recovery_times) / len(recovery_times), 1)
    return 0.0

def get_smart_insights(db_session):
    df_logs = get_habit_logs_df(db_session)
    insights = []
    if df_logs.empty:
        return ["Not enough data for insights."]
        
    completed = df_logs[df_logs['status'] == 'completed']
    
    # Best day of week
    if not completed.empty:
        completed['weekday'] = completed['log_date'].dt.day_name()
        best_day = completed['weekday'].value_counts().idxmax()
        insights.append(f"🔥 Your most productive day is **{best_day}**.")
        
    # Recovery metric
    rec_time = calculate_recovery_metrics(db_session)
    if rec_time > 0:
        insights.append(f"🔄 Average bounce-back time after missing a habit is **{rec_time} days**.")
        
    # Keystone Habit Detection (Dependency Analysis)
    # Compare overall day productivity when a specific habit is completed vs missed
    habits = db_session.query(Habit).filter(Habit.is_active == True).all()
    if len(habits) > 1 and not df_logs.empty:
        # Group by date to get daily productivity score (total habits completed that day)
        daily_prod = completed.groupby('log_date').size().reset_index(name='daily_completions')
        
        keystone = None
        max_diff = 0
        best_stats = (0, 0)
        
        for h in habits:
            h_logs = df_logs[df_logs['habit_id'] == h.id]
            if h_logs.empty: continue
            
            completed_dates = h_logs[h_logs['status'] == 'completed']['log_date']
            missed_dates = h_logs[h_logs['status'] == 'missed']['log_date']
            
            if not completed_dates.empty and not missed_dates.empty:
                # Avg completions on days this habit was completed
                avg_completed_when_done = daily_prod[daily_prod['log_date'].isin(completed_dates)]['daily_completions'].mean()
                # Avg completions on days this habit was missed
                avg_completed_when_missed = daily_prod[daily_prod['log_date'].isin(missed_dates)]['daily_completions'].mean()
                
                # Convert to percentage of total habits
                if pd.isna(avg_completed_when_done): avg_completed_when_done = 0
                if pd.isna(avg_completed_when_missed): avg_completed_when_missed = 0
                
                pct_when_done = (avg_completed_when_done / len(habits)) * 100
                pct_when_missed = (avg_completed_when_missed / len(habits)) * 100
                
                diff = pct_when_done - pct_when_missed
                if diff > max_diff and diff > 10: # Minimum 10% difference to be significant
                    max_diff = diff
                    keystone = h.name
                    best_stats = (int(pct_when_done), int(pct_when_missed))
                    
        if keystone:
            insights.append(f"🔑 **Keystone Habit Detected:** Overall productivity is **{best_stats[0]}%** when you complete **{keystone}**, but drops to **{best_stats[1]}%** when missed.")

    # Data quality
    total_logs = len(df_logs)
    if total_logs > 0:
        missed_with_reason = len(df_logs[(df_logs['status'] == 'missed') & (df_logs['missed_reason'] != "")])
        total_missed = len(df_logs[df_logs['status'] == 'missed'])
        if total_missed > 0:
            quality = int((missed_with_reason / total_missed) * 100)
            insights.append(f"📊 Habit logging consistency for missed reasons is **{quality}%**.")
            
    return insights if insights else ["Keep logging data to generate insights!"]
