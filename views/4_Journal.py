import streamlit as st
from datetime import date
from database import get_db_session
from services.journal_service import (
    get_daily_journal, save_daily_journal, delete_daily_journal,
    get_weekly_review, save_weekly_review, delete_weekly_review,
    get_monthly_reflection, save_monthly_reflection, delete_monthly_reflection
)


st.title("Life Journal & Reviews")

db = get_db_session()
today = date.today()

tab1, tab2, tab3 = st.tabs(["Daily Journal", "Weekly Review", "Monthly Reflection"])

# 1. Daily Journal
with tab1:
    st.subheader(f"Daily Entry: {today.strftime('%b %d, %Y')}")
    journal = get_daily_journal(db, today)
    
    with st.form("daily_journal_form"):
        col1, col2 = st.columns(2)
        with col1:
            mood = st.selectbox("Mood", ["😊 Happy", "😌 Calm", "😐 Neutral", "😔 Sad", "😠 Frustrated", "😴 Tired"], index=0 if not journal.mood else ["😊 Happy", "😌 Calm", "😐 Neutral", "😔 Sad", "😠 Frustrated", "😴 Tired"].index(journal.mood) if journal.mood in ["😊 Happy", "😌 Calm", "😐 Neutral", "😔 Sad", "😠 Frustrated", "😴 Tired"] else 0)
            energy = st.slider("Energy Level (1-10)", 1, 10, value=journal.energy if journal.energy else 5)
            sleep = st.number_input("Sleep (Hours)", min_value=0.0, max_value=24.0, step=0.5, value=float(journal.sleep_hours) if journal.sleep_hours else 7.0)
        with col2:
            focus = st.slider("Focus Score (1-10)", 1, 10, value=journal.focus_score if journal.focus_score else 5)
            stress = st.slider("Stress Level (1-10)", 1, 10, value=journal.stress_score if journal.stress_score else 3)
        
        c_notes1, c_notes2 = st.columns(2)
        with c_notes1:
            wins = st.text_area("Wins", value=journal.wins, height=100)
            learnings = st.text_area("Learnings", value=journal.learnings, height=100)
        with c_notes2:
            blockers = st.text_area("Blockers", value=journal.blockers, height=100)
            distractions = st.text_area("Distractions", value=journal.distractions, height=100)
            
        notes = st.text_area("Brain Dump / General Notes", value=journal.notes)
        
        if st.form_submit_button("Save Daily Entry"):
            save_daily_journal(db, today, mood, energy, sleep, focus, stress, notes, wins, blockers, learnings, distractions)
            st.success("Daily journal saved!")
            
    if journal.id:
        if st.button("Delete Daily Entry", type="primary"):
            delete_daily_journal(db, today)
            st.rerun()

# 2. Weekly Review
with tab2:
    st.subheader("Weekly Review")
    st.caption("Reflect on the past 7 days to calibrate for the next.")
    review = get_weekly_review(db, today)
    
    with st.form("weekly_review_form"):
        wins = st.text_area("What worked well? (Weekly Wins)", value=review.wins)
        failures = st.text_area("What failed? (Weekly Failures)", value=review.failures)
        distractions = st.text_area("Biggest Distraction", value=review.distractions)
        priority = st.text_input("Priority for Next Week", value=review.next_week_priority)
        
        if st.form_submit_button("Save Weekly Review"):
            save_weekly_review(db, today, wins, failures, distractions, priority)
            st.success("Weekly review saved!")
            
    if review.id:
        if st.button("Delete Weekly Review", type="primary"):
            delete_weekly_review(db, today)
            st.rerun()

# 3. Monthly Reflection
with tab3:
    st.subheader(f"Monthly Reflection: {today.strftime('%B %Y')}")
    reflection = get_monthly_reflection(db, today.year, today.month)
    
    with st.form("monthly_reflection_form"):
        m_wins = st.text_area("Biggest wins this month?", value=reflection.wins)
        m_improvements = st.text_area("Biggest lessons / Improvements needed?", value=reflection.improvements)
        m_notes = st.text_area("General Notes", value=reflection.notes)
        
        if st.form_submit_button("Save Monthly Reflection"):
            save_monthly_reflection(db, today.year, today.month, m_wins, m_improvements, m_notes)
            st.success("Monthly reflection saved!")
            
    if reflection.id:
        if st.button("Delete Monthly Reflection", type="primary"):
            delete_monthly_reflection(db, today.year, today.month)
            st.rerun()

db.close()
