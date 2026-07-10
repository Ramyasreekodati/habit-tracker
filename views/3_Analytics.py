import streamlit as st
import altair as alt
from datetime import date
from database import get_db_session
from services.analytics_service import (
    get_habit_logs_df,
    generate_heatmap_data,
    calculate_success_rates,
    calculate_forecasting,
    calculate_recovery_metrics
)



st.title("Analytics")

db = get_db_session()

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

db.close()
