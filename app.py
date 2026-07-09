import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import calendar
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dateutil.relativedelta import relativedelta

# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------
engine = create_engine("sqlite:///growthos.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    monthly_goal = Column(Integer, default=20)
    reward = Column(String)
    frequency_type = Column(String, default="daily")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    log_date = Column(String, index=True) # ISO format: YYYY-MM-DD
    status = Column(String, default="") # Enum: "", "completed", "missed", "skipped"
    note = Column(String)
    habit = relationship("Habit")

Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    if db.query(Habit).count() == 0:
        default_habits = [
            {"name": "Python Study", "category": "Career", "monthly_goal": 20, "reward": "Buy new mechanical keyboard", "display_order": 1},
            {"name": "SQL Practice", "category": "Career", "monthly_goal": 15, "reward": "Nice Dinner", "display_order": 2},
            {"name": "Exercise", "category": "Health", "monthly_goal": 22, "reward": "New gym shirt", "display_order": 3},
            {"name": "Meditation", "category": "Health", "monthly_goal": 30, "reward": "Relaxing weekend", "display_order": 4},
            {"name": "Read 10 pages", "category": "Learning", "monthly_goal": 25, "reward": "Buy new book", "display_order": 5}
        ]
        # set created_at to 2 months ago for testing
        past_date = datetime.utcnow() - timedelta(days=60)
        for h in default_habits:
            habit = Habit(**h)
            habit.created_at = past_date
            db.add(habit)
        db.commit()
    db.close()

seed_db()

# ---------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------
def get_streak(logs_df, habit_id):
    # Sort dates descending
    h_logs = logs_df[logs_df['habit_id'] == habit_id].sort_values('log_date', ascending=False)
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    today_str = date.today().isoformat()
    
    # Calculate streaks chronologically
    h_logs_asc = h_logs.sort_values('log_date', ascending=True)
    for _, row in h_logs_asc.iterrows():
        if row['log_date'] > today_str:
            continue # ignore future dates
            
        if row['status'] == "completed":
            temp_streak += 1
            if temp_streak > best_streak:
                best_streak = temp_streak
        elif row['status'] == "missed":
            temp_streak = 0
        elif row['status'] == "skipped":
            pass # streak pauses, doesn't break

    # Current streak calculation (working backwards from today)
    # We need to find if the streak is currently alive.
    # If yesterday was missed and today is empty, streak is 0.
    
    # A robust way is to just use the temp_streak from chronological loop 
    # IF the most recent past days haven't broken it.
    # To handle empty days in the past: if a day before today is empty, does it break the streak?
    # Yes, an empty past day is essentially a 'miss' if not explicitly marked skipped.
    
    # For MVP, we will just count backwards from today.
    # Generate list of dates from today backwards
    c_streak = 0
    check_date = date.today()
    while True:
        d_str = check_date.isoformat()
        row = h_logs[h_logs['log_date'] == d_str]
        if not row.empty:
            status = row.iloc[0]['status']
            if status == "completed":
                c_streak += 1
            elif status == "skipped":
                pass # skip over it
            else:
                # Missed or empty string "" -> breaks streak
                if d_str != today_str: # if today is empty, it shouldn't break yesterday's streak yet
                    break
        else:
             if d_str != today_str:
                 break
        check_date -= timedelta(days=1)

    return c_streak, best_streak

# ---------------------------------------------------------
# UI CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="GrowthOS Tracker", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #202124; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 600; color: #1f1f1f; }
    .metric-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 2px rgba(60,64,67,0.3); text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("GrowthOS Portfolio Tracker")

# State Management for Month Navigation
if 'current_date' not in st.session_state:
    st.session_state.current_date = date.today().replace(day=1)

db = SessionLocal()

# Month Navigation UI
col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
with col_nav1:
    if st.button("← Previous Month"):
        st.session_state.current_date = st.session_state.current_date - relativedelta(months=1)
        st.rerun()
with col_nav2:
    st.markdown(f"<h3 style='text-align: center;'>{calendar.month_name[st.session_state.current_date.month]} {st.session_state.current_date.year}</h3>", unsafe_allow_html=True)
with col_nav3:
    if st.button("Next Month →"):
        st.session_state.current_date = st.session_state.current_date + relativedelta(months=1)
        st.rerun()

year = st.session_state.current_date.year
month = st.session_state.current_date.month
num_days = calendar.monthrange(year, month)[1]

habits = db.query(Habit).filter(Habit.is_active == True).order_by(Habit.display_order).all()

# Load all logs for streak calculations
all_logs = db.query(HabitLog).all()
df_all_logs = pd.DataFrame([{"habit_id": l.habit_id, "log_date": l.log_date, "status": l.status} for l in all_logs])

# ---------------------------------------------------------
# THE GRID
# ---------------------------------------------------------
st.markdown("### Tracker Grid")
st.caption("✅ = Completed | ❌ = Missed | ⏭️ = Skipped")

# Build mapping for rendering
status_map = {"completed": "✅", "missed": "❌", "skipped": "⏭️", "": ""}
rev_status_map = {"✅": "completed", "❌": "missed", "⏭️": "skipped", "": ""}

days_list = [f"{d}" for d in range(1, num_days + 1)]
df_data = {}

# We need row-level metrics
habit_metrics = {}

for h in habits:
    row_data = {
        "Goal": h.monthly_goal,
        "Progress": "",
        "Streak (Cur / Best)": "",
        "Reward": h.reward
    }
    
    completed_this_month = 0
    
    for d in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{d:02d}"
        if not df_all_logs.empty:
            match = df_all_logs[(df_all_logs['habit_id'] == h.id) & (df_all_logs['log_date'] == date_str)]
            status = match.iloc[0]['status'] if not match.empty else ""
            row_data[str(d)] = status_map.get(status, "")
            if status == "completed":
                completed_this_month += 1
        else:
            row_data[str(d)] = ""
            
    # Calculate Progress %
    progress_pct = (completed_this_month / h.monthly_goal) * 100 if h.monthly_goal > 0 else 0
    row_data["Progress"] = f"{int(progress_pct)}%"
    
    # Calculate Streaks
    if not df_all_logs.empty:
        c_streak, b_streak = get_streak(df_all_logs, h.id)
    else:
        c_streak, b_streak = 0, 0
    row_data["Streak (Cur / Best)"] = f"{c_streak} / {b_streak}"
    
    df_data[h.name] = row_data

df = pd.DataFrame.from_dict(df_data, orient='index')

# Column configuration
col_config = {
    "Goal": st.column_config.NumberColumn("Goal", disabled=True),
    "Progress": st.column_config.TextColumn("Progress", disabled=True),
    "Streak (Cur / Best)": st.column_config.TextColumn("Streaks", disabled=True),
    "Reward": st.column_config.TextColumn("Reward", disabled=True)
}
for d in days_list:
    col_config[d] = st.column_config.SelectboxColumn(d, options=["", "✅", "❌", "⏭️"], default="")

edited_df = st.data_editor(
    df,
    use_container_width=True,
    height=400,
    column_config=col_config
)

# Detect and Save Changes
for h in habits:
    for d in range(1, num_days + 1):
        day_str = str(d)
        is_val = edited_df.loc[h.name, day_str]
        was_val = df.loc[h.name, day_str]
        
        if is_val != was_val:
            date_str = f"{year}-{month:02d}-{d:02d}"
            mapped_status = rev_status_map.get(is_val, "")
            
            log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.log_date == date_str).first()
            if log:
                log.status = mapped_status
            else:
                log = HabitLog(habit_id=h.id, log_date=date_str, status=mapped_status)
                db.add(log)
            db.commit()

# ---------------------------------------------------------
# ANALYTICS SECTION
# ---------------------------------------------------------
st.markdown("### 📈 Analytics")

# Daily Summary for Today
today_str = date.today().isoformat()
today_logs = []
if not df_all_logs.empty:
    today_logs = df_all_logs[df_all_logs['log_date'] == today_str]

completed_today = len(today_logs[today_logs['status'] == 'completed']) if not isinstance(today_logs, list) else 0
total_active = len(habits)
productivity = (completed_today / total_active * 100) if total_active > 0 else 0

col_a1, col_a2, col_a3 = st.columns(3)
col_a1.markdown(f'<div class="metric-card"><h2>{completed_today}</h2><p>Completed Today</p></div>', unsafe_allow_html=True)
col_a2.markdown(f'<div class="metric-card"><h2>{total_active - completed_today}</h2><p>Remaining Today</p></div>', unsafe_allow_html=True)
col_a3.markdown(f'<div class="metric-card"><h2 style="color:#2ea043">{int(productivity)}%</h2><p>Productivity</p></div>', unsafe_allow_html=True)

st.write("---")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("**Daily Completion Trend**")
    # Count ✅ per day from edited_df
    daily_sums = []
    for d in days_list:
        count = sum(1 for h in habits if edited_df.loc[h.name, d] == "✅")
        daily_sums.append(count)
        
    df_daily = pd.DataFrame({"Day": days_list, "Completed": daily_sums})
    fig_bar = px.bar(df_daily, x="Day", y="Completed", color="Completed", color_continuous_scale="Greens")
    fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_c2:
    st.markdown("**Category Performance**")
    cat_data = {}
    for h in habits:
        if h.category not in cat_data:
            cat_data[h.category] = {"completed": 0, "total": h.monthly_goal}
        else:
            cat_data[h.category]["total"] += h.monthly_goal
            
        count_completed = sum(1 for d in days_list if edited_df.loc[h.name, d] == "✅")
        cat_data[h.category]["completed"] += count_completed
        
    df_cat = pd.DataFrame([
        {"Category": k, "Progress %": (v["completed"] / v["total"] * 100) if v["total"] > 0 else 0}
        for k, v in cat_data.items()
    ])
    
    if not df_cat.empty:
        fig_pie = px.pie(df_cat, names="Category", values="Progress %", hole=0.5)
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

db.close()
