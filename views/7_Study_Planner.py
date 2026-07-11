import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
from database import get_db_session
from services.study_service import (
    get_subjects, add_subject, get_study_sessions, 
    add_study_session, update_session_status, delete_study_session
)
from services.goal_service import get_monthly_goals, get_weekly_plans

st.title("Study Planner")
st.caption("Plan, track, and review your learning journey.")

db = get_db_session()
today = date.today()

# Tabs
tab_planner, tab_subjects = st.tabs(["Planner", "Subjects"])

with tab_subjects:
    st.subheader("Subject Master")
    subjects = get_subjects(db)
    
    if not subjects:
        st.info("No subjects defined yet.")
    else:
        # Display existing subjects
        for s in subjects:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{s.name}** ({s.category})")
                with col2:
                    st.write(f"Estimated: {s.estimated_total_hours} hrs")
                with col3:
                    if s.is_completed:
                        st.success("Completed")
                    else:
                        st.info("Active")
    
    st.write("---")
    st.subheader("Add New Subject")
    with st.form("add_subject_form"):
        name = st.text_input("Name (e.g. SQL Fundamentals)")
        category = st.selectbox("Category", ["Programming", "Business", "Math", "Science", "Other"])
        est_hours = st.number_input("Estimated Total Hours", min_value=1, value=20)
        priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: {1: "High", 2: "Medium", 3: "Low"}[x])
        color = st.color_picker("Color", "#4CAF50")
        
        if st.form_submit_button("Add Subject") and name:
            add_subject(db, name, category, priority, est_hours, color)
            st.rerun()

with tab_planner:
    st.subheader(f"Today's Plan ({today.strftime('%b %d')})")
    
    # Load goals for linking
    curr_ym = f"{today.year}-{today.month:02d}"
    monthlies = {m.id: m.goal_text for m in get_monthly_goals(db, curr_ym)}
    weeklies = {w.id: w.task_text for w in get_weekly_plans(db, curr_ym)}
    
    # Existing sessions for today
    sessions = get_study_sessions(db, start_date=today, end_date=today)
    
    if not sessions:
        st.info("No study sessions planned for today.")
    else:
        for sess in sessions:
            with st.container(border=True):
                sc1, sc2, sc3 = st.columns([3, 2, 2])
                with sc1:
                    subject_name = sess.subject.name if sess.subject else "Unknown"
                    st.markdown(f"**{subject_name}** - {sess.topic}")
                    st.caption(f"{sess.session_type} | {sess.duration_minutes} mins")
                with sc2:
                    status_color = {"planned": "orange", "completed": "green", "skipped": "red"}.get(sess.status, "gray")
                    st.markdown(f"Status: <span style='color:{status_color}'>{sess.status.title()}</span>", unsafe_allow_html=True)
                with sc3:
                    if sess.status == 'planned':
                        if st.button("Mark Completed", key=f"comp_{sess.id}"):
                            # Simplistic completion for now
                            update_session_status(db, sess.id, "completed", completion_date=today)
                            st.rerun()
                        if st.button("Skip", key=f"skip_{sess.id}"):
                            update_session_status(db, sess.id, "skipped")
                            st.rerun()
                    if st.button("Delete", key=f"del_sess_{sess.id}"):
                        delete_study_session(db, sess.id)
                        st.rerun()
                        
    st.write("---")
    st.subheader("Add Study Session")
    
    if not subjects:
        st.warning("Please add a subject first in the Subjects tab.")
    else:
        with st.form("add_session_form"):
            s_date = st.date_input("Date", value=today)
            s_subject = st.selectbox("Subject", subjects, format_func=lambda x: x.name)
            s_topic = st.text_input("Topic")
            s_duration = st.number_input("Duration (minutes)", min_value=15, step=15, value=60)
            
            c1, c2 = st.columns(2)
            with c1:
                s_type = st.selectbox("Session Type", ["Learning", "Practice", "Revision", "Project", "Mock Interview"])
            with c2:
                s_source = st.selectbox("Source Type", ["Udemy", "YouTube", "Book", "Practice", "College", "Personal Notes", "Other"])
                
            g1, g2 = st.columns(2)
            with g1:
                m_goal = st.selectbox("Link Monthly Goal (Optional)", [None] + list(monthlies.keys()), format_func=lambda x: monthlies.get(x, "None"))
            with g2:
                w_plan = st.selectbox("Link Weekly Plan (Optional)", [None] + list(weeklies.keys()), format_func=lambda x: weeklies.get(x, "None"))
                
            if st.form_submit_button("Plan Session") and s_topic:
                add_study_session(
                    db, 
                    planned_date=s_date, 
                    subject_id=s_subject.id, 
                    topic=s_topic, 
                    duration_minutes=s_duration,
                    session_type=s_type,
                    source_type=s_source,
                    monthly_goal_id=m_goal,
                    weekly_plan_id=w_plan
                )
                st.rerun()

db.close()
