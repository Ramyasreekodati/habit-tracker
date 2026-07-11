import streamlit as st
import os

st.set_page_config(
    page_title="GrowthOS",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the whole app
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #202124; }
    h1, h2, h3, h4, h5 { font-family: 'Inter', sans-serif; font-weight: 600; color: #1f1f1f; }
    .metric-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 2px rgba(60,64,67,0.3); text-align: center; }
    .kpi-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(60,64,67,0.1); text-align: center; height: 100%; border-top: 4px solid #1a73e8; }
    .kpi-value { font-size: 3rem; font-weight: bold; color: #1a73e8; margin-bottom: 0;}
    .kpi-label { font-size: 1.1rem; color: #5f6368; margin-top: 0; text-transform: uppercase; letter-spacing: 1px;}
    .quote-box { background: #e8f0fe; padding: 25px; border-left: 5px solid #1a73e8; border-radius: 4px; font-style: italic; font-size: 1.2rem; color: #1a73e8; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.write("---")
    st.caption("GrowthOS v3.0 | Database v3")
    with st.expander("🛠️ Admin & Backups"):
        if os.path.exists("growthos.db"):
            with open("growthos.db", "rb") as f:
                db_data = f.read()
            st.download_button("Export Database", data=db_data, file_name="growthos_backup.db", mime="application/octet-stream")
        
        uploaded_db = st.file_uploader("Restore Database", type=["db", "sqlite"])
        if uploaded_db:
            if st.button("Confirm Restore", type="primary"):
                with open("growthos.db", "wb") as f:
                    f.write(uploaded_db.getbuffer())
                st.success("Database restored! Please reload the page.")

pages = {
    "Overview": [
        st.Page("views/1_Dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
        st.Page("views/2_Tracker.py", title="Tracker", icon=":material/check_box:"),
    ],
    "Learning": [
        st.Page("views/7_Study_Planner.py", title="Study Planner", icon=":material/school:"),
        st.Page("views/8_Revision.py", title="Revision Queue", icon=":material/menu_book:"),
    ],
    "Insights": [
        st.Page("views/3_Analytics.py", title="Analytics", icon=":material/analytics:"),
        st.Page("views/5_Reports.py", title="Reports", icon=":material/summarize:"),
    ],
    "Life": [
        st.Page("views/4_Journal.py", title="Journal", icon=":material/book:"),
        st.Page("views/6_Goals.py", title="Goals", icon=":material/flag:"),
    ]
}

pg = st.navigation(pages)
pg.run()
