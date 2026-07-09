import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import calendar
import random
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from io import BytesIO

# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------
engine = create_engine("sqlite:///growthos.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        CheckConstraint('monthly_goal > 0', name='check_goal_positive'),
    )
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
    __table_args__ = (
        CheckConstraint("status IN ('', 'completed', 'missed', 'skipped')", name='check_valid_status'),
        UniqueConstraint('habit_id', 'log_date', name='uq_habit_date'),
    )
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    log_date = Column(String, index=True) 
    status = Column(String, default="")
    note = Column(String)
    habit = relationship("Habit")

class MonthlyGoal(Base):
    __tablename__ = "monthly_goals"
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String, index=True) # YYYY-MM
    goal_text = Column(String)
    completed = Column(Boolean, default=False)

class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String, index=True)
    week_number = Column(Integer) # 1-5
    task_text = Column(String)
    completed = Column(Boolean, default=False)

class MonthlyReflection(Base):
    __tablename__ = "monthly_reflections"
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String, index=True, unique=True)
    wins = Column(String, default="")
    improvements = Column(String, default="")
    notes = Column(String, default="")

Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    if db.query(Habit).count() == 0:
        default_habits = [
            {"name": "Python Study", "category": "Career", "monthly_goal": 20, "reward": "Mechanical Keyboard", "display_order": 1},
            {"name": "SQL Practice", "category": "Career", "monthly_goal": 15, "reward": "Nice Dinner", "display_order": 2},
            {"name": "Exercise", "category": "Health", "monthly_goal": 22, "reward": "New Gym Shirt", "display_order": 3},
            {"name": "Meditation", "category": "Health", "monthly_goal": 30, "reward": "Relaxing Weekend", "display_order": 4},
            {"name": "Read 10 pages", "category": "Learning", "monthly_goal": 25, "reward": "Buy New Book", "display_order": 5}
        ]
        past_date = datetime.utcnow() - timedelta(days=60)
        for h in default_habits:
            habit = Habit(**h)
            habit.created_at = past_date
            db.add(habit)
            
        curr_ym = f"{date.today().year}-{date.today().month:02d}"
        db.add(MonthlyGoal(year_month=curr_ym, goal_text="Finish ML Course", completed=False))
        db.add(MonthlyGoal(year_month=curr_ym, goal_text="Build Portfolio Website", completed=False))
        db.add(WeeklyPlan(year_month=curr_ym, week_number=1, task_text="Learn SQL Joins", completed=True))
        db.add(WeeklyPlan(year_month=curr_ym, week_number=2, task_text="Apply to Internships", completed=False))
        
        db.add(MonthlyReflection(year_month=curr_ym, wins="Consistency with reading.", improvements="Need to sleep earlier.", notes="Exams this month made it hard."))
            
        db.commit()
    db.close()

seed_db()

# ---------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------
def get_streak(logs_df, habit_id):
    h_logs = logs_df[logs_df['habit_id'] == habit_id].sort_values('log_date', ascending=False)
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    today_str = date.today().isoformat()
    
    h_logs_asc = h_logs.sort_values('log_date', ascending=True)
    for _, row in h_logs_asc.iterrows():
        if row['log_date'] > today_str:
            continue 
        if row['status'] == "completed":
            temp_streak += 1
            if temp_streak > best_streak:
                best_streak = temp_streak
        elif row['status'] == "missed":
            temp_streak = 0
            
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
                pass
            else:
                if d_str != today_str: 
                    break
        else:
             if d_str != today_str:
                 break
        check_date -= timedelta(days=1)
    return c_streak, best_streak

QUOTES = [
    "The beginning is the most important part of the work.",
    "We are what we repeatedly do. Excellence, then, is not an act, but a habit.",
    "Success is the product of daily habits—not once-in-a-lifetime transformations.",
    "You do not rise to the level of your goals. You fall to the level of your systems."
]

# ---------------------------------------------------------
# UI CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="GrowthOS Portfolio", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #202124; }
    h1, h2, h3, h4, h5 { font-family: 'Inter', sans-serif; font-weight: 600; color: #1f1f1f; }
    .metric-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 2px rgba(60,64,67,0.3); text-align: center; }
    .kpi-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(60,64,67,0.1); text-align: center; height: 100%; border-top: 4px solid #1a73e8; }
    .kpi-value { font-size: 3rem; font-weight: bold; color: #1a73e8; margin-bottom: 0;}
    .kpi-label { font-size: 1.1rem; color: #5f6368; margin-top: 0; text-transform: uppercase; letter-spacing: 1px;}
    .quote-box { background: #e8f0fe; padding: 25px; border-left: 5px solid #1a73e8; border-radius: 4px; font-style: italic; font-size: 1.2rem; color: #1a73e8; margin-bottom: 20px;}
    .footer { text-align: center; color: #9aa0a6; font-size: 0.8rem; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

st.title("GrowthOS Habit Dashboard")
db = SessionLocal()

# State Management for Navigation
if 'sel_year' not in st.session_state:
    st.session_state.sel_year = date.today().year
if 'sel_month' not in st.session_state:
    st.session_state.sel_month = date.today().month

# Nav & Export Row
col_nav1, col_nav2, col_export = st.columns([1, 1, 2])
with col_nav1:
    year = st.selectbox("Year", range(2020, 2030), index=range(2020, 2030).index(st.session_state.sel_year))
    st.session_state.sel_year = year
with col_nav2:
    months_names = list(calendar.month_name)[1:]
    month_name = st.selectbox("Month", months_names, index=st.session_state.sel_month - 1)
    month = months_names.index(month_name) + 1
    st.session_state.sel_month = month
    
num_days = calendar.monthrange(year, month)[1]
curr_ym = f"{year}-{month:02d}"

# CRUD Expander
with st.expander("⚙️ Manage Habits & Data"):
    tab1, tab2, tab3 = st.tabs(["Add Habit", "Archive/Restore", "Import / Restore Data"])
    
    with tab1:
        with st.form("add_habit_form"):
            c1, c2, c3 = st.columns(3)
            h_name = c1.text_input("Name")
            h_cat = c2.selectbox("Category", ["Health", "Career", "Learning", "Personal"])
            h_goal = c3.number_input("Monthly Goal (Days)", min_value=1, max_value=31, value=20)
            h_reward = st.text_input("Reward for achieving goal")
            if st.form_submit_button("Add Habit"):
                if h_name:
                    new_h = Habit(name=h_name, category=h_cat, monthly_goal=h_goal, reward=h_reward, created_at=datetime.utcnow())
                    db.add(new_h)
                    db.commit()
                    st.rerun()

    with tab2:
        all_h = db.query(Habit).all()
        for h in all_h:
            colA, colB = st.columns([4,1])
            colA.write(f"{h.name} ({'Active' if h.is_active else 'Archived'})")
            btn_label = "Archive" if h.is_active else "Restore"
            if colB.button(btn_label, key=f"toggle_{h.id}"):
                h.is_active = not h.is_active
                db.commit()
                st.rerun()
                
    with tab3:
        st.write("Restore from Database Backup (.db)")
        uploaded_file = st.file_uploader("Upload SQLite Database Backup", type=['db', 'sqlite'])
        if uploaded_file is not None:
            if st.button("Restore Database"):
                with open("growthos.db", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Database restored successfully! Please refresh the page.")

habits = db.query(Habit).filter(Habit.is_active == True).order_by(Habit.display_order).all()

if not habits:
    st.warning("No active habits found. Open 'Manage Habits' to create your first habit!")
    st.stop()

# Load logs
all_logs = db.query(HabitLog).all()
df_all_logs = pd.DataFrame([{"habit_id": l.habit_id, "log_date": l.log_date, "status": l.status} for l in all_logs])

# ---------------------------------------------------------
# THE GRID
# ---------------------------------------------------------
st.markdown("### Tracker Grid")
st.caption("✅ = Completed | ❌ = Missed | ⏭️ = Skipped | N/A = Not Created Yet")

status_map = {"completed": "✅", "missed": "❌", "skipped": "⏭️", "": ""}
rev_status_map = {"✅": "completed", "❌": "missed", "⏭️": "skipped", "": "", "N/A": ""}

days_list = [f"{d}" for d in range(1, num_days + 1)]
df_data = {}

total_completions_this_month = 0
total_goals_achieved = 0
master_best_streak = 0

for h in habits:
    row_data = {
        "Goal": h.monthly_goal,
        "Progress": 0.0,
        "Streak": "",
        "Reward": ""
    }
    
    completed_this_month = 0
    h_created_date = h.created_at.date()
    
    for d in range(1, num_days + 1):
        cell_date = date(year, month, d)
        date_str = cell_date.isoformat()
        
        if cell_date < h_created_date:
            row_data[str(d)] = "N/A"
        else:
            if not df_all_logs.empty:
                match = df_all_logs[(df_all_logs['habit_id'] == h.id) & (df_all_logs['log_date'] == date_str)]
                status = match.iloc[0]['status'] if not match.empty else ""
                row_data[str(d)] = status_map.get(status, "")
                if status == "completed":
                    completed_this_month += 1
                    total_completions_this_month += 1
            else:
                row_data[str(d)] = ""
                
    progress_pct = min((completed_this_month / h.monthly_goal), 1.0) if h.monthly_goal > 0 else 0
    row_data["Progress"] = progress_pct
    
    if completed_this_month >= h.monthly_goal:
        total_goals_achieved += 1
        row_data["Reward"] = f"🎁 {h.reward} (Unlocked!)"
    else:
        row_data["Reward"] = f"🔒 {h.reward}"
    
    if not df_all_logs.empty:
        c_streak, b_streak = get_streak(df_all_logs, h.id)
    else:
        c_streak, b_streak = 0, 0
        
    if b_streak > master_best_streak:
        master_best_streak = b_streak
        
    row_data["Streak"] = f"{c_streak} / {b_streak}"
    
    df_data[h.name] = row_data

df = pd.DataFrame.from_dict(df_data, orient='index')

# Streamlit ProgressColumn for Sparklines!
col_config = {
    "Goal": st.column_config.NumberColumn("Goal", disabled=True),
    "Progress": st.column_config.ProgressColumn(
        "Progress (Sparkline)",
        help="Monthly goal progress",
        format="%.2f",
        min_value=0,
        max_value=1,
    ),
    "Streak": st.column_config.TextColumn("Streaks", disabled=True),
    "Reward": st.column_config.TextColumn("Reward", disabled=True)
}
for d in days_list:
    col_config[d] = st.column_config.SelectboxColumn(d, options=["", "✅", "❌", "⏭️", "N/A"])

edited_df = st.data_editor(df, use_container_width=True, height=350, column_config=col_config)

# Export Data Buttons
with col_export:
    c1, c2 = st.columns(2)
    csv = df.to_csv()
    c1.download_button(label="📥 Export Grid CSV", data=csv, file_name=f'tracker_{curr_ym}.csv', mime='text/csv')
    with open("growthos.db", "rb") as f:
        c2.download_button(label="📦 Export SQLite DB Backup", data=f, file_name=f'growthos_backup_{curr_ym}.db', mime='application/octet-stream')


# Save grid changes
for h in habits:
    h_created_date = h.created_at.date()
    for d in range(1, num_days + 1):
        cell_date = date(year, month, d)
        if cell_date < h_created_date:
            continue
            
        day_str = str(d)
        is_val = edited_df.loc[h.name, day_str]
        was_val = df.loc[h.name, day_str]
        
        if is_val != was_val and is_val != "N/A":
            date_str = cell_date.isoformat()
            mapped_status = rev_status_map.get(is_val, "")
            log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.log_date == date_str).first()
            if log:
                log.status = mapped_status
            else:
                log = HabitLog(habit_id=h.id, log_date=date_str, status=mapped_status)
                db.add(log)
            db.commit()

# ---------------------------------------------------------
# DAILY SUMMARY ROW
# ---------------------------------------------------------
today_str = date.today().isoformat()
today_logs = []
if not df_all_logs.empty:
    today_logs = df_all_logs[df_all_logs['log_date'] == today_str]

c_today = len(today_logs[today_logs['status'] == 'completed']) if not isinstance(today_logs, list) else 0
m_today = len(today_logs[today_logs['status'] == 'missed']) if not isinstance(today_logs, list) else 0
prod_today = (c_today / len(habits) * 100) if len(habits) > 0 else 0

st.markdown("#### Daily Summary (Today)")
sc1, sc2, sc3 = st.columns(3)
sc1.metric("Completed Today", c_today)
sc2.metric("Missed Today", m_today)
sc3.metric("Productivity %", f"{int(prod_today)}%")
st.write("---")

# ---------------------------------------------------------
# LOWER DASHBOARD (Goals, Planning, Reflections, KPIs)
# ---------------------------------------------------------
st.markdown("### Monthly Dashboard")

lb_left, lb_mid, lb_right = st.columns([1, 1, 1.5])

with lb_left:
    st.markdown("**Monthly Goals**")
    m_goals = db.query(MonthlyGoal).filter(MonthlyGoal.year_month == curr_ym).all()
    for mg in m_goals:
        checked = st.checkbox(mg.goal_text, value=mg.completed, key=f"mg_{mg.id}")
        if checked != mg.completed:
            mg.completed = checked
            db.commit()
    with st.form("new_mg"):
        g_txt = st.text_input("New Goal")
        if st.form_submit_button("Add Goal") and g_txt:
            db.add(MonthlyGoal(year_month=curr_ym, goal_text=g_txt))
            db.commit()
            st.rerun()

with lb_mid:
    st.markdown("**Weekly Planning**")
    w_plans = db.query(WeeklyPlan).filter(WeeklyPlan.year_month == curr_ym).order_by(WeeklyPlan.week_number).all()
    for wp in w_plans:
        checked = st.checkbox(f"W{wp.week_number}: {wp.task_text}", value=wp.completed, key=f"wp_{wp.id}")
        if checked != wp.completed:
            wp.completed = checked
            db.commit()
    with st.form("new_wp"):
        wp_wk = st.number_input("Week", min_value=1, max_value=5, value=1)
        wp_txt = st.text_input("New Task")
        if st.form_submit_button("Add Task") and wp_txt:
            db.add(WeeklyPlan(year_month=curr_ym, week_number=wp_wk, task_text=wp_txt))
            db.commit()
            st.rerun()

with lb_right:
    # Quote
    st.markdown(f"<div class='quote-box'>\"{random.choice(QUOTES)}\"</div>", unsafe_allow_html=True)
    
    # KPIs
    kpi_col1, kpi_col2 = st.columns(2)
    with kpi_col1:
        st.markdown(f"<div class='kpi-card'><p class='kpi-value'>{total_completions_this_month}</p><p class='kpi-label'>Total Completions</p></div>", unsafe_allow_html=True)
    with kpi_col2:
        achieved_pct = (total_goals_achieved / len(habits) * 100) if habits else 0
        st.markdown(f"<div class='kpi-card'><p class='kpi-value'>{achieved_pct:.1f}%</p><p class='kpi-label'>Goals Achieved</p></div>", unsafe_allow_html=True)

st.write("---")
# Monthly Reflections
st.markdown("### Monthly Reflection Notes")
reflection = db.query(MonthlyReflection).filter(MonthlyReflection.year_month == curr_ym).first()
if not reflection:
    reflection = MonthlyReflection(year_month=curr_ym)
    db.add(reflection)
    db.commit()

with st.form("reflection_form"):
    r_wins = st.text_area("What worked well this month?", value=reflection.wins)
    r_improvements = st.text_area("What needs improvement?", value=reflection.improvements)
    r_notes = st.text_area("General Notes / Overrides", value=reflection.notes)
    if st.form_submit_button("Save Reflections"):
        reflection.wins = r_wins
        reflection.improvements = r_improvements
        reflection.notes = r_notes
        db.commit()
        st.success("Reflections saved!")

# Footer Data Ownership
st.markdown(f"<div class='footer'>Data Ownership Metadata<br>Total Habits Tracked: {len(db.query(Habit).all())} | Master Best Streak: {master_best_streak} days | Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</div>", unsafe_allow_html=True)

db.close()
