import streamlit as st
import altair as alt
from datetime import date
from database import get_db_session
from services.analytics_service import (
    get_smart_insights, get_dashboard_kpis, get_todays_tasks, 
    get_category_performance, get_weekly_trend, get_recent_activity
)

st.title("LifeOS Dashboard")

db = get_db_session()
today = date.today()

# 1. KPI Cards
with st.spinner("Loading KPIs..."):
    kpis = get_dashboard_kpis(db, today)
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    c1.metric("Today's Score", f"{kpis['today_pct']}%")
    c2.metric("Weekly Score", f"{kpis['week_score']}%")
    c3.metric("Longest Streak", f"{kpis['longest_streak']} days")
    c4.metric("Goal Alignment", f"{kpis['goal_alignment']}%")
    c5.metric("Mood", kpis['mood'])
    c6.metric("Sleep", f"{kpis['sleep']}h")
    
st.write("---")

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📋 Today's Focus")
    tasks = get_todays_tasks(db, today)
    if not tasks:
        st.info("No active habits for today. Go to Tracker to add some!")
    else:
        for t in tasks:
            status_icon = "✅" if t['status'] == "completed" else "❌" if t['status'] == "missed" else "⏭️" if t['status'] == "skipped" else "⬜"
            st.markdown(f"{status_icon} **{t['name']}**  `{t['category']}`")
            
    st.write("---")
    st.subheader("📈 Weekly Trend")
    with st.spinner("Generating trend..."):
        trend_df = get_weekly_trend(db, today)
        if not trend_df.empty:
            chart = alt.Chart(trend_df).mark_area(
                line={'color': '#1f77b4'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1f77b4', offset=0),
                           alt.GradientStop(color='white', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('date', sort=None, title=""),
                y=alt.Y('score', title="Completion %", scale=alt.Scale(domain=[0, 100])),
                tooltip=['date', 'score']
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Not enough data to show weekly trend.")

with col_right:
    st.subheader("📊 Category Performance")
    with st.spinner("Crunching numbers..."):
        cat_df = get_category_performance(db)
        if not cat_df.empty:
            pie_chart = alt.Chart(cat_df).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="completions", type="quantitative"),
                color=alt.Color(field="category", type="nominal", legend=alt.Legend(title="Category")),
                tooltip=['category', 'completions']
            ).properties(height=250)
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("No completions recorded yet.")
            
    st.write("---")
    st.subheader("⏱️ Recent Activity")
    activities = get_recent_activity(db)
    if not activities:
        st.info("No recent activity.")
    else:
        for act in activities:
            icon = "✅" if act['status'] == 'completed' else "❌"
            reason = f" ({act['reason']})" if act['reason'] else ""
            st.markdown(f"{icon} **{act['habit']}** on {act['date'].strftime('%b %d')}{reason}")

st.write("---")
st.subheader("💡 Smart Insights")
insights = get_smart_insights(db)
for insight in insights:
    st.info(insight)

db.close()
