import streamlit as st
from database import get_db_session
from services.analytics_service import get_smart_insights, calculate_recovery_metrics, get_habit_logs_df
from models import Habit

st.set_page_config(page_title="Dashboard | GrowthOS", page_icon="📈", layout="wide")

st.title("Today's Focus")

db = get_db_session()

# Calculate some high level stats
habits = db.query(Habit).filter(Habit.is_active == True).all()
total_active = len(habits)

st.markdown("### Executive Overview")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.metric("Active Habits", total_active)

with col2:
    with st.container(border=True):
        rec_time = calculate_recovery_metrics(db)
        st.metric("Avg Bounce-back", f"{rec_time} days")

with col3:
    with st.container(border=True):
        st.metric("Current Streaks", "Available in Tracker", "View Grid")

st.markdown("### Smart Insights")
insights = get_smart_insights(db)
for insight in insights:
    st.info(insight)

db.close()
