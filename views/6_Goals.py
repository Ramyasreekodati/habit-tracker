import streamlit as st
from datetime import date
from database import get_db_session
from services.goal_service import (
    get_annual_goals, add_annual_goal, update_annual_goal_progress, edit_annual_goal, delete_annual_goal,
    get_monthly_goals, add_monthly_goal, update_monthly_goal_status, update_monthly_goal_progress, delete_monthly_goal,
    get_weekly_plans, add_weekly_plan, update_weekly_plan_status, delete_weekly_plan,
    calculate_goal_alignment
)

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
    if not annuals:
        st.info("No annual goals yet.")
    for a in annuals:
        with st.container(border=True):
            st.markdown(f"**{a.title}**")
            st.caption(a.description)
            st.progress(a.progress / 100.0, text=f"{a.progress}%")
            
            with st.expander("Edit / Delete"):
                with st.form(f"edit_ag_{a.id}"):
                    e_title = st.text_input("Title", value=a.title)
                    e_desc = st.text_input("Description", value=a.description)
                    if st.form_submit_button("Update"):
                        edit_annual_goal(db, a.id, e_title, e_desc)
                        st.rerun()
                if st.button("Delete Goal", key=f"del_ag_{a.id}", type="primary"):
                    delete_annual_goal(db, a.id)
                    st.rerun()
                
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
    if not monthlies:
        st.info("No monthly goals yet.")
    for m in monthlies:
        mc1, mc2 = st.columns([5, 1])
        with mc1:
            st.markdown(f"**{m.goal_text}** (Weight: {m.weight})")
            if m.progress_mode == "manual":
                prog = st.slider("Progress", 0, 100, m.progress, key=f"mg_prog_{m.id}")
                if prog != m.progress:
                    update_monthly_goal_progress(db, m.id, prog)
                    st.rerun()
            else:
                st.progress(m.progress / 100.0, text=f"Auto Progress: {m.progress}%")
        with mc2:
            if st.button("🗑️", key=f"del_mg_{m.id}", help="Delete Monthly Goal"):
                delete_monthly_goal(db, m.id)
                st.rerun()
        st.write("---")
        
    with st.form("add_monthly"):
        m_txt = st.text_input("New Monthly Goal")
        
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            p_mode = st.selectbox("Progress Mode", ["manual", "automatic"], help="Automatic goals track progress based on weekly plans.")
        with m_c2:
            m_weight = st.number_input("Goal Weight", min_value=1, max_value=10, value=1, help="Used for weighted annual progress calculation.")
        
        annual_opts = {0: "None"}
        annuals_all = get_annual_goals(db, current_year)
        for an in annuals_all:
            annual_opts[an.id] = an.title
        selected_a = st.selectbox("Link to Annual Goal", options=list(annual_opts.keys()), format_func=lambda x: annual_opts[x])
        
        if st.form_submit_button("Add Goal") and m_txt:
            add_monthly_goal(db, curr_ym, m_txt, selected_a if selected_a != 0 else None, p_mode, m_weight)
            st.rerun()

# 3. Weekly Plans
with col_c:
    st.subheader("Weekly Plans")
    weeklies = get_weekly_plans(db, curr_ym)
    if not weeklies:
        st.info("No weekly plans yet.")
    for w in weeklies:
        wc1, wc2 = st.columns([5, 1])
        with wc1:
            checked = st.checkbox(f"W{w.week_number}: {w.task_text}", value=w.completed, key=f"wp_{w.id}")
            if checked != w.completed:
                update_weekly_plan_status(db, w.id, checked)
                st.rerun()
        with wc2:
            if st.button("🗑️", key=f"del_wp_{w.id}", help="Delete Weekly Plan"):
                delete_weekly_plan(db, w.id)
                st.rerun()
        
    with st.form("add_weekly"):
        w_num = st.number_input("Week", min_value=1, max_value=5, value=1)
        w_txt = st.text_input("New Task")
        
        monthly_opts = {0: "None"}
        monthlies_all = get_monthly_goals(db, curr_ym)
        for mo in monthlies_all:
            monthly_opts[mo.id] = mo.goal_text
        selected_m = st.selectbox("Link to Monthly Goal", options=list(monthly_opts.keys()), format_func=lambda x: monthly_opts[x])
        
        if st.form_submit_button("Add Task") and w_txt:
            add_weekly_plan(db, curr_ym, w_num, w_txt, selected_m if selected_m != 0 else None)
            st.rerun()

db.close()
