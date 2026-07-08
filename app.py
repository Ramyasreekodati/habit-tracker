import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px

st.set_page_config(page_title="GrowthOS", layout="wide", page_icon="🌱")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    h1, h2, h3 { color: #e2e8f0 !important; font-weight: 800 !important; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 5px; backdrop-filter: blur(10px); gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; font-weight: 600; border-radius: 8px !important; padding: 10px 20px !important; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] { background: rgba(99, 102, 241, 0.2) !important; color: #c7d2fe !important; border: 1px solid rgba(99,102,241,0.5) !important; }
    .stNumberInput input, .stTextInput input, .stDateInput input, .stTextArea textarea { background: rgba(15,23,42,0.6) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #f1f5f9 !important; border-radius: 8px !important; }
    [data-testid="metric-container"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 15px; }
    .stButton > button { background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# --- Database ---
def init_db():
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    # Daily Logs V3 (Added Deep Work & Failure Journal)
    c.execute('''CREATE TABLE IF NOT EXISTS daily_logs_v3 (
        date TEXT UNIQUE, sleep_hours REAL, water_glasses INTEGER, walking_mins INTEGER, exercise_mins INTEGER, meditation_mins INTEGER,
        genai_modules INTEGER, mba_chapters INTEGER, python_notebooks INTEGER, sql_problems INTEGER, dsa_problems INTEGER,
        git_commits INTEGER, features_built INTEGER, apps_sent INTEGER, interviews INTEGER, resume_updates INTEGER,
        focus_score INTEGER, energy_score INTEGER, distractions INTEGER,
        journal_good TEXT, journal_fail TEXT, journal_why TEXT, journal_tomorrow TEXT
    )''')
    # Knowledge Debt
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge_debt (
        id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, status TEXT
    )''')
    # Weekly Output Artifacts
    c.execute('''CREATE TABLE IF NOT EXISTS output_artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, artifact_name TEXT, url TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def load_logs():
    conn = sqlite3.connect('growthos.db')
    df = pd.read_sql_query("SELECT * FROM daily_logs_v3 ORDER BY date DESC", conn)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

# --- UI ---
st.title("🚀 GrowthOS: Elite Execution")
st.markdown("*Systems over goals. Output over consumption.*")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Daily Execution", "🚨 Analytics & Red Flags", "🧠 Knowledge & Output", "📅 Master Schedule"])

with tab1:
    st.header("Log Today's Execution")
    date_input = st.date_input("Date", datetime.date.today())
    
    st.subheader("1. Deep Work & Recovery")
    c1, c2, c3, c4 = st.columns(4)
    focus = c1.slider("Focus Quality (1-5)", 1, 5, 3)
    energy = c2.slider("Energy Level (1-5)", 1, 5, 3)
    distractions = c3.number_input("Distractions (Count)", 0, 50, 0)
    sleep = c4.number_input("Sleep (Hours)", 0.0, 24.0, 7.5, 0.5)
    
    st.subheader("2. Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        water = st.number_input("Water (Glasses)", 0, 20, 9)
        walk = st.number_input("Walking (Mins)", 0, 300, 45, 5)
        exercise = st.number_input("Exercise (Mins)", 0, 180, 20, 5)
        meditation = st.number_input("Meditation (Mins)", 0, 120, 15, 5)
    with c2:
        genai = st.number_input("GenAI Modules", 0, 10, 0)
        mba = st.number_input("MBA Chapters", 0, 10, 0)
        python = st.number_input("Python Notebooks", 0, 10, 0)
        sql = st.number_input("SQL Problems", 0, 50, 0)
        dsa = st.number_input("DSA Problems", 0, 20, 0)
    with c3:
        commits = st.number_input("Git Commits", 0, 50, 0)
        features = st.number_input("Features Built", 0, 10, 0)
    with c4:
        apps = st.number_input("Applications Sent", 0, 100, 0)
        interviews = st.number_input("Interviews", 0, 5, 0)
        resume = st.number_input("Resume Updates", 0, 5, 0)
        
    st.subheader("3. Failure Journal (Highest ROI)")
    j1, j2 = st.columns(2)
    j_good = j1.text_area("What went well today?")
    j_fail = j1.text_area("What failed today?")
    j_why = j2.text_area("Why did it fail?")
    j_tmrw = j2.text_area("What changes tomorrow?")
    
    if st.button("Save Daily Execution"):
        execute_query('''
            INSERT INTO daily_logs_v3 (date, sleep_hours, water_glasses, walking_mins, exercise_mins, meditation_mins, genai_modules, mba_chapters, python_notebooks, sql_problems, dsa_problems, git_commits, features_built, apps_sent, interviews, resume_updates, focus_score, energy_score, distractions, journal_good, journal_fail, journal_why, journal_tomorrow)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(date) DO UPDATE SET sleep_hours=excluded.sleep_hours, water_glasses=excluded.water_glasses, walking_mins=excluded.walking_mins, exercise_mins=excluded.exercise_mins, meditation_mins=excluded.meditation_mins, genai_modules=excluded.genai_modules, mba_chapters=excluded.mba_chapters, python_notebooks=excluded.python_notebooks, sql_problems=excluded.sql_problems, dsa_problems=excluded.dsa_problems, git_commits=excluded.git_commits, features_built=excluded.features_built, apps_sent=excluded.apps_sent, interviews=excluded.interviews, resume_updates=excluded.resume_updates, focus_score=excluded.focus_score, energy_score=excluded.energy_score, distractions=excluded.distractions, journal_good=excluded.journal_good, journal_fail=excluded.journal_fail, journal_why=excluded.journal_why, journal_tomorrow=excluded.journal_tomorrow
        ''', (str(date_input), sleep, water, walk, exercise, meditation, genai, mba, python, sql, dsa, commits, features, apps, interviews, resume, focus, energy, distractions, j_good, j_fail, j_why, j_tmrw))
        st.success("Execution & Journal saved! Consistency compounds.")

with tab2:
    st.header("🚨 Red Flags & Analytics")
    df = load_logs()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        recent_3 = df.head(3)
        recent_5 = df.head(5)
        recent_7 = df.head(7)
        
        # Red Flags
        st.subheader("System Warnings")
        if recent_3['sleep_hours'].mean() < 6.0 and len(recent_3) == 3:
            st.error("🚨 **RED FLAG:** Sleep < 6 hours for 3 days. High burnout risk.")
        
        coding_sum = recent_5['python_notebooks'].sum() + recent_5['dsa_problems'].sum() + recent_5['sql_problems'].sum()
        if coding_sum == 0 and len(recent_5) >= 5:
            st.error("🚨 **RED FLAG:** No coding for 5 days. Knowledge decay accelerating.")
            
        if recent_7['features_built'].sum() == 0 and len(recent_7) >= 7:
            st.warning("⚠️ **Warning:** No project progress for 7 days.")
            
        st.divider()
        st.subheader("Deep Work Quality")
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Focus Score", f"{df['focus_score'].mean():.1f} / 5")
        c2.metric("Avg Energy Score", f"{df['energy_score'].mean():.1f} / 5")
        c3.metric("Avg Distractions", f"{df['distractions'].mean():.1f} / day")
        
        st.divider()
        st.subheader("Output Goals (Last 7 Days)")
        h1, h2, h3 = st.columns(3)
        h1.metric("Git Commits", recent_7['git_commits'].sum())
        h2.metric("Features Built", recent_7['features_built'].sum())
        h3.metric("Problems Solved (SQL+DSA)", recent_7['sql_problems'].sum() + recent_7['dsa_problems'].sum())
        
        st.divider()
        fig = px.line(df.sort_values('date'), x='date', y=['focus_score', 'energy_score'], title="Energy vs Focus Correlation")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log data to activate the Red Flag system.")

with tab3:
    st.header("🧠 Knowledge Debt & Output Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Knowledge Debt Tracker")
        st.markdown("*Topics you don't fully understand yet.*")
        with st.form("debt_form"):
            new_topic = st.text_input("New Topic (e.g. Attention Mechanism)")
            if st.form_submit_button("Add Debt"):
                execute_query("INSERT INTO knowledge_debt (topic, status) VALUES (?, ?)", (new_topic, "❌ Pending"))
                st.success("Added to debt list.")
                
        conn = sqlite3.connect('growthos.db')
        debt_df = pd.read_sql_query("SELECT * FROM knowledge_debt", conn)
        conn.close()
        for _, row in debt_df.iterrows():
            st.markdown(f"{row['status']} **{row['topic']}**")
            
    with col2:
        st.subheader("Weekly Public Artifact")
        st.markdown("*Every week, create ONE artifact that can be shown to another person.*")
        with st.form("artifact_form"):
            art_name = st.text_input("Artifact Name (e.g. RAG Chatbot Repo)")
            art_url = st.text_input("Public URL")
            if st.form_submit_button("Log Output Artifact"):
                execute_query("INSERT INTO output_artifacts (date, artifact_name, url) VALUES (?, ?, ?)", (str(datetime.date.today()), art_name, art_url))
                st.success("Artifact recorded! You are building public proof.")
                
        conn = sqlite3.connect('growthos.db')
        art_df = pd.read_sql_query("SELECT * FROM output_artifacts ORDER BY date DESC", conn)
        conn.close()
        for _, row in art_df.iterrows():
            st.markdown(f"✅ {row['date']}: [{row['artifact_name']}]({row['url']})")

with tab4:
    st.header("📅 Master Schedule & Targets")
    st.markdown("""
    ### 🛡️ Non-Negotiable Buffer
    Reserve 30-60 minutes daily (e.g., 9:30 PM - 10:00 PM) for life's chaos. Unused buffer = bonus study time.
    
    ### 🛑 Weekly No-Course Day (Sunday)
    * NO new courses. NO new videos.
    * ONLY revision, projects, and backlog clearance.
    
    ### 💼 Monthly Career Day
    * Half a day every month dedicated to: Resume, LinkedIn, Portfolio, GitHub cleanup, Applications.
    
    ### 💧 Water Schedule (9 Glasses)
    4:00 AM | 5:45 AM | 8:00 AM | 10:00 AM | 1:00 PM | 3:00 PM | 5:00 PM | 7:00 PM | 9:00 PM
    
    ### ⏱️ Energy-Based Daily Routine
    * **4:00 - 4:15**: Meditation (Mental Clarity)
    * **4:15 - 5:00**: Aptitude (High Energy)
    * **5:00 - 5:45**: Programming Practice (High Energy)
    * **8:00 - 10:00**: GenAI Main Course (High Energy)
    * **10:00 - 11:00**: Implementation (Medium Energy)
    * **4:00 - 5:30**: Data Science Project (Medium Energy)
    * **5:30 - 6:30**: Secondary Course (Low Energy)
    * **8:15 - 9:15**: Project Improvement (Medium Energy)
    * **9:15 - 10:00**: DSA Problem (High Energy)
    * **10:15 PM**: Sleep
    """)
