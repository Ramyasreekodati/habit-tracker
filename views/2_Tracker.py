import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import calendar
from database import get_db_session
from models import Habit, HabitLog

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
    tab_add, tab_edit, tab_archive = st.tabs(["Add Habit", "Edit Habit", "Archived Habits"])
    
    with tab_add:
        with st.form("add_habit_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            h_name = c1.text_input("Name")
            h_cat = c2.selectbox("Category", ["Health", "Career", "Learning", "Personal"])
            h_goal = c3.number_input("Monthly Goal (Days)", min_value=1, max_value=31, value=20)
            # Reward removed as per request
            h_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            diff_map = {"Easy": 1, "Medium": 2, "Hard": 3}

            if st.form_submit_button("Add Habit"):
                if h_name:
                    try:
                        new_h = Habit(
                            name=h_name, 
                            category=h_cat, 
                            monthly_goal=h_goal, 
                            reward="", 
                            difficulty=diff_map[h_diff]
                        )
                        db.add(new_h)
                        db.commit()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error adding habit: {e}")

    with tab_edit:
        active_habits = db.query(Habit).filter(Habit.is_active == True).order_by(Habit.display_order).all()
        if active_habits:
            edit_h_id = st.selectbox("Select Habit to Edit", [h.id for h in active_habits], format_func=lambda x: next(h.name for h in active_habits if h.id == x))
            edit_h = next((h for h in active_habits if h.id == edit_h_id), None)
            
            if edit_h:
                with st.form("edit_habit_form"):
                    c1, c2, c3 = st.columns(3)
                    e_name = c1.text_input("Name", value=edit_h.name)
                    cats = ["Health", "Career", "Learning", "Personal"]
                    e_cat = c2.selectbox("Category", cats, index=cats.index(edit_h.category) if edit_h.category in cats else 0)
                    e_goal = c3.number_input("Monthly Goal (Days)", min_value=1, max_value=31, value=edit_h.monthly_goal)
                    # Reward removed as per request
                    
                    diffs = ["Easy", "Medium", "Hard"]
                    rev_diff_map = {1: "Easy", 2: "Medium", 3: "Hard"}
                    curr_diff = rev_diff_map.get(edit_h.difficulty, "Easy")
                    e_diff = st.selectbox("Difficulty", diffs, index=diffs.index(curr_diff))

                    col_u, col_a = st.columns(2)
                    update_btn = col_u.form_submit_button("Update Habit", type="primary")
                    archive_btn = col_a.form_submit_button("Archive Habit")

                    if update_btn:
                        try:
                            edit_h.name = e_name
                            edit_h.category = e_cat
                            edit_h.monthly_goal = e_goal
                            edit_h.reward = ""
                            edit_h.difficulty = diff_map[e_diff]
                            db.commit()
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error updating: {e}")
                    
                    if archive_btn:
                        try:
                            edit_h.is_active = False
                            db.commit()
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error archiving: {e}")
        else:
            st.info("No active habits to edit.")
            
    with tab_archive:
        archived_habits = db.query(Habit).filter(Habit.is_active == False).all()
        if archived_habits:
            for arch_h in archived_habits:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{arch_h.name}** ({arch_h.category})")
                if c2.button("Restore", key=f"res_{arch_h.id}"):
                    try:
                        arch_h.is_active = True
                        db.commit()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error restoring: {e}")
                if c3.button("Delete Forever", key=f"del_{arch_h.id}", type="primary"):
                    try:
                        db.delete(arch_h)
                        db.commit()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error deleting: {e}")
        else:
            st.info("No archived habits.")


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
        "Habit": h.name,
        "Goal": h.monthly_goal,
        "Progress": 0.0
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
    
    # Reward logic removed
    
    # Use ID + Name as index to prevent duplicates from overwriting
    df_data[f"{h.id}_{h.name}"] = row_data

df = pd.DataFrame.from_dict(df_data, orient='index')

# Make the visual column names cleaner
col_config = {
    "Habit": st.column_config.TextColumn("Habit", disabled=True),
    "Goal": st.column_config.NumberColumn("Goal", disabled=True),
    "Progress": st.column_config.ProgressColumn(
        "Progress",
        format="%.2f",
        min_value=0,
        max_value=1,
    )
}
for d in days_list:
    col_config[d] = st.column_config.SelectboxColumn(d, options=["", "✅", "❌", "⏭️", "N/A"])

# Render the data editor
edited_df = st.data_editor(
    df, 
    use_container_width=True, 
    height=350, 
    column_config=col_config,
    hide_index=True # Hide the ugly ID_Name index from the user
)

# Save changes to the database
changes_made = False
for h in habits:
    h_created_date = h.created_at.date()
    idx = f"{h.id}_{h.name}"
    for d in range(1, num_days + 1):
        cell_date = date(year, month, d)
        if cell_date < h_created_date:
            continue
            
        day_str = str(d)
        is_val = edited_df.loc[idx, day_str]
        was_val = df.loc[idx, day_str]
        
        is_val = "" if is_val is None else is_val
        was_val = "" if was_val is None else was_val
        
        if is_val != was_val and is_val != "N/A":
            mapped_status = rev_status_map.get(is_val, "")
            log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.log_date == cell_date).first()
            if log:
                log.status = mapped_status
            else:
                log = HabitLog(habit_id=h.id, log_date=cell_date, status=mapped_status)
                db.add(log)
            changes_made = True

# Commit once outside the loop
if changes_made:
    try:
        db.commit()
        st.rerun()
    except Exception as e:
        db.rollback()
        st.error(f"Error saving logs: {e}")

# --- Weekly Progress Pie Charts ---
st.markdown("### Weekly Progress")
st.caption("Your completion rate for each week of the selected month.")

import altair as alt

# Group days into weeks for the selected month
weeks = {}
for d in range(1, num_days + 1):
    cell_date = date(year, month, d)
    week_num = (d - 1) // 7 + 1
    if week_num not in weeks:
        weeks[week_num] = {"completed": 0, "total": 0}
    
    for h in habits:
        h_created_date = h.created_at.date()
        if cell_date >= h_created_date:
            weeks[week_num]["total"] += 1
            idx = f"{h.id}_{h.name}"
            # Check the status in the dataframe (handles unsaved edits as well)
            if df_data.get(idx, {}).get(str(d)) == "✅":
                weeks[week_num]["completed"] += 1

# Render charts side by side
cols = st.columns(len(weeks))
for idx, (week_num, stats) in enumerate(weeks.items()):
    with cols[idx]:
        st.markdown(f"**Week {week_num}**")
        if stats["total"] > 0:
            pct = int((stats["completed"] / stats["total"]) * 100)
            remaining = 100 - pct
            source = pd.DataFrame({
                "Status": ["Achieved", "Remaining"],
                "Value": [pct, remaining]
            })
            
            base = alt.Chart(source).encode(
                theta=alt.Theta("Value:Q", stack=True),
                color=alt.Color("Status:N", scale=alt.Scale(domain=["Achieved", "Remaining"], range=["#28a745", "#e9ecef"]), legend=None),
                tooltip=["Status", "Value"]
            )
            
            pie = base.mark_arc(innerRadius=30, stroke="#fff")
            text = base.mark_text(radius=0, size=14, fontWeight="bold").encode(text=alt.value(f"{pct}%"))
            
            st.altair_chart(pie + text, use_container_width=True)
        else:
            st.info("No data")

db.close()
