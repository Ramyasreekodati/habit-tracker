import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import calendar
from database import get_db_session
from models import Habit, HabitLog

st.set_page_config(page_title="Tracker | GrowthOS", page_icon="✅", layout="wide")

st.title("Habit Tracker")

db = get_db_session()

# Initialize session state for navigation
if 'sel_year' not in st.session_state:
    st.session_state.sel_year = date.today().year
if 'sel_month' not in st.session_state:
    st.session_state.sel_month = date.today().month

col_nav1, col_nav2 = st.columns(2)
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
with st.expander("⚙️ Manage Habits"):
    with st.form("add_habit_form"):
        c1, c2, c3 = st.columns(3)
        h_name = c1.text_input("Name")
        h_cat = c2.selectbox("Category", ["Health", "Career", "Learning", "Personal"])
        h_goal = c3.number_input("Monthly Goal (Days)", min_value=1, max_value=31, value=20)
        h_reward = st.text_input("Reward for achieving goal")
        
        # Difficulty points: Easy=1, Medium=2, Hard=3
        h_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        diff_map = {"Easy": 1, "Medium": 2, "Hard": 3}

        if st.form_submit_button("Add Habit"):
            if h_name:
                new_h = Habit(
                    name=h_name, 
                    category=h_cat, 
                    monthly_goal=h_goal, 
                    reward=h_reward, 
                    created_at=datetime.utcnow(),
                    difficulty=diff_map[h_diff]
                )
                db.add(new_h)
                db.commit()
                st.rerun()

habits = db.query(Habit).filter(Habit.is_active == True).order_by(Habit.display_order).all()

if not habits:
    st.warning("No active habits found. Open 'Manage Habits' to create your first habit!")
    st.stop()

# Load logs
# Fetch logs for the selected month to optimize query
start_date = date(year, month, 1)
end_date = date(year, month, num_days)
all_logs = db.query(HabitLog).filter(HabitLog.log_date >= start_date, HabitLog.log_date <= end_date).all()
df_all_logs = pd.DataFrame([{"habit_id": l.habit_id, "log_date": l.log_date, "status": l.status} for l in all_logs])

st.markdown("### Tracker Grid")
st.caption("✅ = Completed | ❌ = Missed | ⏭️ = Skipped | N/A = Not Created Yet")

status_map = {"completed": "✅", "missed": "❌", "skipped": "⏭️", "": ""}
rev_status_map = {"✅": "completed", "❌": "missed", "⏭️": "skipped", "": "", "N/A": ""}

days_list = [f"{d}" for d in range(1, num_days + 1)]
df_data = {}

for h in habits:
    row_data = {
        "Goal": h.monthly_goal,
        "Progress": 0.0,
        "Reward": ""
    }
    
    completed_this_month = 0
    h_created_date = h.created_at.date()
    
    for d in range(1, num_days + 1):
        cell_date = date(year, month, d)
        
        if cell_date < h_created_date:
            row_data[str(d)] = "N/A"
        else:
            if not df_all_logs.empty:
                match = df_all_logs[(df_all_logs['habit_id'] == h.id) & (df_all_logs['log_date'] == cell_date)]
                status = match.iloc[0]['status'] if not match.empty else ""
                row_data[str(d)] = status_map.get(status, "")
                if status == "completed":
                    completed_this_month += 1
            else:
                row_data[str(d)] = ""
                
    progress_pct = min((completed_this_month / h.monthly_goal), 1.0) if h.monthly_goal > 0 else 0
    row_data["Progress"] = progress_pct
    
    if completed_this_month >= h.monthly_goal:
        row_data["Reward"] = f"🎁 {h.reward} (Unlocked!)"
    else:
        row_data["Reward"] = f"🔒 {h.reward}"
    
    df_data[h.name] = row_data

df = pd.DataFrame.from_dict(df_data, orient='index')

col_config = {
    "Goal": st.column_config.NumberColumn("Goal", disabled=True),
    "Progress": st.column_config.ProgressColumn(
        "Progress",
        format="%.2f",
        min_value=0,
        max_value=1,
    ),
    "Reward": st.column_config.TextColumn("Reward", disabled=True)
}
for d in days_list:
    col_config[d] = st.column_config.SelectboxColumn(d, options=["", "✅", "❌", "⏭️", "N/A"])

edited_df = st.data_editor(df, use_container_width=True, height=350, column_config=col_config)

# Save changes to the database
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
            mapped_status = rev_status_map.get(is_val, "")
            log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.log_date == cell_date).first()
            if log:
                log.status = mapped_status
            else:
                log = HabitLog(habit_id=h.id, log_date=cell_date, status=mapped_status)
                db.add(log)
            db.commit()

db.close()
