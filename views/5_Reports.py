import streamlit as st
from datetime import date
import calendar
from database import get_db_session
from services.report_service import generate_monthly_report, generate_csv_report



st.title("Monthly Reports")

db = get_db_session()
today = date.today()

col1, col2 = st.columns([1, 3])
with col1:
    sel_year = st.selectbox("Year", range(2020, 2030), index=range(2020, 2030).index(today.year))
    months_names = list(calendar.month_name)[1:]
    month_name = st.selectbox("Month", months_names, index=today.month - 1)
    sel_month = months_names.index(month_name) + 1

with col2:
    if st.button("Generate Report", type="primary"):
        report = generate_monthly_report(db, sel_year, sel_month)
        
        st.markdown(f"### Report for {report['Month']}")
        
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Productivity Score", f"{report.get('Productivity Score', 0)}")
        r2.metric("Success Rate", f"{report.get('Success Rate', 0)}%")
        r3.metric("Total Completions", report.get('Total Completions', 0))
        r4.metric("Habits Tracked", report.get('Total Habits Tracked', 0))
        
        st.write("---")
        
        st.markdown(f"**🏅 Best Habit:** {report.get('Best Habit', 'N/A')}")
        st.markdown(f"**📉 Weakest Habit:** {report.get('Weakest Habit', 'N/A')}")
        st.markdown(f"**🛑 Top Missed Reason:** {report.get('Top Missed Reason', 'N/A')}")
        
        # Export options
        csv_data = generate_csv_report(db, sel_year, sel_month)
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name=f"growthos_report_{sel_year}_{sel_month}.csv",
            mime="text/csv"
        )

db.close()
