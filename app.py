import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px
import time
import random

# --- Config ---
st.set_page_config(page_title="GrowthOS", layout="wide", page_icon="🌱")

# --- Premium Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    h1, h2, h3 { color: #e2e8f0 !important; font-weight: 800 !important; letter-spacing: -0.5px; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 5px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; font-weight: 600; border-radius: 8px !important; padding: 10px 20px !important; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] { background: rgba(99, 102, 241, 0.2) !important; color: #c7d2fe !important; border: 1px solid rgba(99, 102, 241, 0.5) !important; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2); }
    .stNumberInput input, .stTextInput input, .stDateInput input { background: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: #f1f5f9 !important; border-radius: 8px !important; }
    [data-testid="metric-container"] { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 20px; backdrop-filter: blur(10px); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease; }
    [data-testid="metric-container"]:hover { transform: translateY(-5px); border-color: rgba(99, 102, 241, 0.4); }
    .stButton > button { background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 12px 24px !important; transition: transform 0.2s ease, box-shadow 0.2s ease !important; }
    .stButton > button:hover { transform: scale(1.05) !important; box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3) !important; }
</style>
""", unsafe_allow_html=True)

# --- Database Setup (V2 for specific schedule) ---
def init_db():
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            sleep_hours REAL, water_glasses INTEGER, walking_mins INTEGER, exercise_mins INTEGER, meditation_mins INTEGER,
            genai_modules INTEGER, mba_chapters INTEGER, python_notebooks INTEGER, sql_problems INTEGER, dsa_problems INTEGER,
            git_commits INTEGER, features_built INTEGER,
            apps_sent INTEGER, interviews INTEGER, resume_updates INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Helpers ---
def load_data():
    conn = sqlite3.connect('growthos.db')
    df = pd.read_sql_query("SELECT * FROM daily_logs_v2 ORDER BY date DESC", conn)
    conn.close()
    return df

def save_log(data):
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" * len(data))
    updates = ", ".join([f"{k}=excluded.{k}" for k in data.keys() if k != "date"])
    
    query = f'''
        INSERT INTO daily_logs_v2 ({cols}) VALUES ({placeholders})
        ON CONFLICT(date) DO UPDATE SET {updates}
    '''
    c.execute(query, tuple(data.values()))
    conn.commit()
    conn.close()

# --- UI ---
st.title("🚀 GrowthOS: Data Science Mastery")
st.markdown("*Your personal operating system for mastering Data Science & GenAI while avoiding burnout.*")

tab1, tab2, tab3 = st.tabs(["📝 Daily Execution", "📊 Analytics & Targets", "📅 Master Schedule"])

with tab1:
    st.header("Log Today's Execution")
    date_input = st.date_input("Date", datetime.date.today())
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("🧘 Health")
        sleep = st.number_input("Sleep (Hours)", 0.0, 24.0, 7.5, 0.5)
        water = st.number_input("Water (Glasses)", 0, 20, 9)
        walk = st.number_input("Walking (Mins)", 0, 300, 45, 5)
        exercise = st.number_input("Exercise (Mins)", 0, 180, 20, 5)
        meditation = st.number_input("Meditation (Mins)", 0, 120, 15, 5)
        
    with col2:
        st.subheader("📚 Learning")
        genai = st.number_input("GenAI Modules", 0, 10, 0)
        mba = st.number_input("MBA Chapters", 0, 10, 0)
        python = st.number_input("Python Notebooks", 0, 10, 0)
        sql = st.number_input("SQL Problems", 0, 50, 0)
        dsa = st.number_input("DSA Problems", 0, 20, 0)
        
    with col3:
        st.subheader("🛠️ Output")
        commits = st.number_input("Git Commits", 0, 50, 0)
        features = st.number_input("Features Built", 0, 10, 0)
        
    with col4:
        st.subheader("🚀 Career")
        apps = st.number_input("Applications Sent", 0, 100, 0)
        interviews = st.number_input("Interviews", 0, 5, 0)
        resume = st.number_input("Resume Updates", 0, 5, 0)
        
    if st.button("Save Daily Execution", type="primary"):
        data = {
            "date": str(date_input), "sleep_hours": sleep, "water_glasses": water, "walking_mins": walk,
            "exercise_mins": exercise, "meditation_mins": meditation, "genai_modules": genai, "mba_chapters": mba,
            "python_notebooks": python, "sql_problems": sql, "dsa_problems": dsa, "git_commits": commits,
            "features_built": features, "apps_sent": apps, "interviews": interviews, "resume_updates": resume
        }
        save_log(data)
        st.success("Execution log saved successfully! Consistency is key. 🌟")

with tab2:
    st.header("Weekly Analytics vs Targets")
    df = load_data()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        recent_7 = df.head(7)
        
        st.subheader("🎯 Weekly Targets Progress")
        c1, c2, c3, c4 = st.columns(4)
        
        # SQL Target: 15-20
        sql_total = recent_7['sql_problems'].sum()
        c1.metric("SQL Problems (Target: 15)", f"{sql_total}/15", f"{sql_total - 15} vs target")
        
        # Python Target: 3
        py_total = recent_7['python_notebooks'].sum()
        c2.metric("Python Notebooks (Target: 3)", f"{py_total}/3", f"{py_total - 3} vs target")
        
        # DSA Target: 5
        dsa_total = recent_7['dsa_problems'].sum()
        c3.metric("DSA Problems (Target: 5)", f"{dsa_total}/5", f"{dsa_total - 5} vs target")
        
        # GenAI Target: 2
        genai_total = recent_7['genai_modules'].sum()
        c4.metric("GenAI Modules (Target: 2)", f"{genai_total}/2", f"{genai_total - 2} vs target")
        
        st.divider()
        st.subheader("🧘 Health Averages (Last 7 Days)")
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Avg Sleep (Target: 7-8)", f"{recent_7['sleep_hours'].mean():.1f} hr")
        h2.metric("Avg Water (Target: 9)", f"{recent_7['water_glasses'].mean():.1f} gl")
        h3.metric("Avg Walk (Target: 45m)", f"{recent_7['walking_mins'].mean():.0f} m")
        h4.metric("Avg Meditation (Target: 15m)", f"{recent_7['meditation_mins'].mean():.0f} m")
        
        st.divider()
        st.subheader("Trends")
        fig = px.line(df.sort_values('date'), x='date', y=['sleep_hours', 'sql_problems', 'python_notebooks'], labels={'value': 'Count/Hours', 'variable': 'Metric'})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet. Go to the Daily Execution tab to log your first day!")

with tab3:
    st.header("📅 Master Schedule & Targets")
    st.markdown("""
    ### 💧 Water Schedule (9 Glasses)
    * **4:00 AM** - Glass 1 | **5:45 AM** - Glass 2 | **8:00 AM** - Glass 3
    * **10:00 AM** - Glass 4 | **1:00 PM** - Glass 5 | **3:00 PM** - Glass 6
    * **5:00 PM** - Glass 7 | **7:00 PM** - Glass 8 | **9:00 PM** - Glass 9
    
    ### ⏱️ Daily Routine
    * **4:00 - 4:15**: Meditation
    * **4:15 - 5:00**: Aptitude
    * **5:00 - 5:45**: Programming Practice (SQL/Python/DSA)
    * **8:00 - 10:00**: GenAI Main Course
    * **10:00 - 11:00**: Implementation Session
    * **11:30 - 1:00**: MBA Learning
    * **4:00 - 5:30**: Data Science Project
    * **5:30 - 6:30**: Secondary Course
    * **8:15 - 9:15**: Project Improvement (Git/Features)
    * **9:15 - 10:00**: DSA Problem
    * **10:15 PM**: Sleep
    
    ### 🔄 Programming Rotation
    * **Mon**: SQL | **Tue**: Python | **Wed**: DSA | **Thu**: SQL | **Fri**: Python | **Sat**: DSA | **Sun**: Revision
    
    ### 📜 Core Rules
    1. Only ONE primary GenAI course at a time.
    2. YouTube is for clarification, not curriculum.
    3. For every 2 hours of learning -> 1 hour implementation.
    """)
