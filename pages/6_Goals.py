import streamlit as st
from datetime import date
from database import get_db_session
from services.goal_service import (
    get_annual_goals, add_annual_goal, update_annual_goal_progress,
    get_monthly_goals, add_monthly_goal,
    get_weekly_plans, add_weekly_plan,
    calculate_goal_alignment
)

st.set_page_config(page_title="Goals | GrowthOS", page_icon="🎯", layout="wide")

st.title("Goal Management")
st.caption("Annual Goal -> Monthly Goal -> Weekly Plan")

db = get_db_session()
today = date.today()
current_year = today.year
curr_ym = f"{today.year}-{today.month:02d}"

# Goal Alignment Score
alignment = calculate_goal_alignment(db)
st.metric("Goal Alignment Score", f"{alignment}%", help="Measures how well your daily habits align with your annual goals.")
st.write("---")

col_a, col_b, col_c = st.columns(3)

# 1. Annual Goals
with col_a:
    st.subheader(f"Annual Goals ({current_year})")
    annuals = get_annual_goals(db, current_year)
    for a in annuals:
        with st.container(border=True):
            st.markdown(f"**{a.title}**")
            st.caption(a.description)
            new_prog = st.slider("Progress", 0, 100, a.progress, key=f"ag_{a.id}")
            if new_prog != a.progress:
                update_annual_goal_progress(db, a.id, new_prog)
                
    with st.form("add_annual"):
        a_title = st.text_input("New Annual Goal")
        a_desc = st.text_input("Description")
        if st.form_submit_button("Add Goal") and a_title:
            add_annual_goal(db, current_year, a_title, a_desc)
            st.rerun()

# 2. Monthly Goals
with col_b:
    st.subheader(f"Monthly Goals ({today.strftime('%b')})")
    monthlies = get_monthly_goals(db, curr_ym)
    for m in monthlies:
        st.checkbox(m.goal_text, value=m.completed, key=f"mg_{m.id}")
        
    with st.form("add_monthly"):
        m_txt = st.text_input("New Monthly Goal")
        if st.form_submit_button("Add Goal") and m_txt:
            add_monthly_goal(db, curr_ym, m_txt)
            st.rerun()

# 3. Weekly Plans
with col_c:
    st.subheader("Weekly Plans")
    weeklies = get_weekly_plans(db, curr_ym)
    for w in weeklies:
        st.checkbox(f"W{w.week_number}: {w.task_text}", value=w.completed, key=f"wp_{w.id}")
        
    with st.form("add_weekly"):
        w_num = st.number_input("Week", min_value=1, max_value=5, value=1)
        w_txt = st.text_input("New Task")
        if st.form_submit_button("Add Task") and w_txt:
            add_weekly_plan(db, curr_ym, w_num, w_txt)
            st.rerun()

db.close()
