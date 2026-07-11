import streamlit as st
import altair as alt
from datetime import date, timedelta
from database import get_db_session
from services.analytics_service import (
    get_habit_logs_df,
    generate_heatmap_data,
    calculate_success_rates,
    calculate_forecasting,
    calculate_recovery_metrics,
    get_category_performance
)
from services.study_analytics_service import (
    get_study_hours_by_subject,
    get_subject_progress,
    get_deep_work_hours,
    get_revision_completion_rate,
    check_burnout_warning
)

st.title("Analytics")

db = get_db_session()

tab_habits, tab_learning = st.tabs(["Habits", "Learning"])

with tab_habits:
    # 1. Heatmap
    st.markdown("### Consistency Heatmap")
    df_logs = get_habit_logs_df(db)
    df_heatmap = generate_heatmap_data(df_logs)

    if not df_heatmap.empty:
        chart = alt.Chart(df_heatmap).mark_rect().encode(
            x=alt.X('week:O', title='Week of Year', axis=alt.Axis(labels=False, ticks=False)),
            y=alt.Y('weekday:O', title='', axis=alt.Axis(labelExpr="datum.value == 0 ? 'Mon' : datum.value == 2 ? 'Wed' : datum.value == 4 ? 'Fri' : ''")),
            color=alt.Color('completions:Q', scale=alt.Scale(scheme='greens'), legend=None),
            tooltip=[alt.Tooltip('log_date:T', title='Date'), alt.Tooltip('completions:Q', title='Habits Completed')]
        ).properties(
            width='container',
            height=200
        ).configure_view(
            strokeWidth=0
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Not enough data to generate heatmap.")

    # 2. Key Metrics Row
    st.markdown("### Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        rec_time = calculate_recovery_metrics(db)
        st.metric("Recovery Time (Bounce-back)", f"{rec_time} days", help="Average days to recover a habit after missing it.")

    # 3. Success Rates
    st.markdown("### Success Rates")
    df_success = calculate_success_rates(db)
    if not df_success.empty:
        st.dataframe(df_success, use_container_width=True, hide_index=True)
    else:
        st.info("No success rate data available.")

    # 4. Forecasting
    st.markdown("### Monthly Forecasting")
    st.caption(f"Projections for {date.today().strftime('%B %Y')}")
    df_forecast = calculate_forecasting(db, date.today().year, date.today().month)
    if not df_forecast.empty:
        st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    else:
        st.info("No forecasting data available for this month.")

    # 5. Weekly Category Breakdown (Pie Chart)
    st.markdown("### This Week's Focus")
    st.caption(f"Category breakdown for the past 7 days.")
    week_ago = date.today() - timedelta(days=6)
    cat_df = get_category_performance(db, start_date=week_ago, end_date=date.today())

    if not cat_df.empty:
        pie_chart = alt.Chart(cat_df).mark_arc(innerRadius=40).encode(
            theta=alt.Theta(field="completions", type="quantitative"),
            color=alt.Color(field="category", type="nominal", legend=alt.Legend(title="Category")),
            tooltip=['category', 'completions']
        ).properties(height=300)
        st.altair_chart(pie_chart, use_container_width=True)
    else:
        st.info("No completions recorded in the past 7 days.")

with tab_learning:
    st.subheader("Learning Analytics")
    
    # Time window (Last 30 Days)
    thirty_days_ago = date.today() - timedelta(days=30)
    
    # 1. Burnout Warning
    burnout = check_burnout_warning(db, date.today())
    if burnout['is_burnout']:
        st.error("⚠️ **Burnout Warning!** You've had a significant drop in study hours, low sleep, and negative mood. Please take a break!")
    elif burnout['hours_drop'] or burnout['low_sleep'] or burnout['negative_streak']:
        warnings = []
        if burnout['hours_drop']: warnings.append("Significant drop in study hours.")
        if burnout['low_sleep']: warnings.append("Low average sleep.")
        if burnout['negative_streak']: warnings.append("Negative mood streak.")
        st.warning("⚠️ **Warning Signs:** " + " | ".join(warnings))
        
    st.write("---")
    
    # 2. Key Metrics
    m1, m2 = st.columns(2)
    with m1:
        dw = get_deep_work_hours(db, thirty_days_ago, date.today())
        st.metric("Deep Work (Last 30 Days)", f"{dw} hrs", help="Total hours from sessions >= 50 minutes")
    with m2:
        rev_rate = get_revision_completion_rate(db, thirty_days_ago, date.today())
        st.metric("Revision Completion Rate", f"{rev_rate}%", help="Percentage of completed revisions out of total due")

    st.write("---")
    
    # 3. Subject Time Investment & Distribution
    st.markdown("### Time Investment & Distribution (Last 30 Days)")
    df_hours = get_study_hours_by_subject(db, thirty_days_ago, date.today())
    
    if not df_hours.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(df_hours, use_container_width=True, hide_index=True)
        with c2:
            pie = alt.Chart(df_hours).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Hours", type="quantitative"),
                color=alt.Color(field="Subject", type="nominal")
            ).properties(height=250)
            st.altair_chart(pie, use_container_width=True)
    else:
        st.info("No study sessions recorded in the last 30 days.")
        
    st.write("---")
    
    # 4. Subject Progress
    st.markdown("### Subject Progress Tracker")
    df_prog = get_subject_progress(db)
    if not df_prog.empty:
        st.dataframe(
            df_prog, 
            column_config={
                "Progress %": st.column_config.ProgressColumn(
                    "Progress",
                    help="Percentage of Target Hours Completed",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                )
            },
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No active subjects.")

db.close()
