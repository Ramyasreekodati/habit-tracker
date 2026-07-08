import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px

# Configuration
st.set_page_config(page_title="GrowthOS V9", page_icon="⚡", layout="wide")

# Theme
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    .stButton>button { background-color: #4f46e5; color: white; font-weight: bold; }
    .metric-box { background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# Database Connection (Reads from the new V9 backend DB if it exists, otherwise local)
def get_db():
    conn = sqlite3.connect("growthos.db")
    # Ensure tables exist for Streamlit if running independently
    conn.execute('''CREATE TABLE IF NOT EXISTS engine_health (date TEXT, sleep REAL, water INTEGER, walk INTEGER, exercise INTEGER, meditation INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS engine_learning_state (id INTEGER PRIMARY KEY, topic TEXT, difficulty INTEGER, importance INTEGER, interview_frequency INTEGER, pipeline_stage TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS engine_sessions (id INTEGER PRIMARY KEY, date TEXT, topic TEXT, start_time TEXT, end_time TEXT, duration_minutes INTEGER, output_quantity INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS engine_projects (id INTEGER PRIMARY KEY, project_name TEXT, feature_name TEXT, status TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS engine_career (id INTEGER PRIMARY KEY, date TEXT, category TEXT, description TEXT, resume_impact TEXT)''')
    return conn

conn = get_db()

st.title("⚡ GrowthOS V9: 5-Layer Execution Engine")

# Navigation
tabs = st.tabs(["⚡ What's Next?", "🧘 L1 Health", "🧠 L2 Learning", "⏱️ L3 Sessions", "📈 L4 Analytics", "🚀 L5 Career"])

# --- L0: ENGINE ---
with tabs[0]:
    st.markdown("### Next High-Priority Task")
    
    # Calculate Priority
    topics_df = pd.read_sql_query("SELECT * FROM engine_learning_state WHERE pipeline_stage != 'Master'", conn)
    
    if not topics_df.empty:
        topics_df['priority'] = topics_df['difficulty'] * topics_df['importance'] * topics_df['interview_frequency']
        best_task = topics_df.loc[topics_df['priority'].idxmax()]
        
        st.info(f"**Highest Priority Task:** {best_task['topic']}")
        st.write(f"**Stage:** {best_task['pipeline_stage']} | **Priority Score:** {best_task['priority']}")
    else:
        st.success("No active learning debt! Focus on projects.")
        
    st.markdown("---")
    st.markdown("### Opportunity Cost Engine")
    sessions_df = pd.read_sql_query("SELECT * FROM engine_sessions", conn)
    if not sessions_df.empty and sessions_df['duration_minutes'].sum() > 0:
        rate = (sessions_df['output_quantity'].sum() / sessions_df['duration_minutes'].sum()) * 60
        st.warning(f"💡 If you spend 2 hours on social media right now, you will lose the opportunity to complete {round(rate * 2, 1)} problems based on your historical velocity.")
    else:
        st.warning("💡 Log more sessions to calculate your actual opportunity cost.")

# --- L1: HEALTH ---
with tabs[1]:
    st.markdown("### Log Health")
    with st.form("health_form"):
        col1, col2, col3 = st.columns(3)
        sleep = col1.number_input("Sleep (hrs)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        water = col2.number_input("Water (glasses)", min_value=0, max_value=20, value=8)
        walk = col3.number_input("Walk (mins)", min_value=0, max_value=300, value=45)
        if st.form_submit_button("Log Health"):
            conn.execute("INSERT INTO engine_health (date, sleep, water, walk, exercise, meditation) VALUES (?, ?, ?, ?, ?, ?)", (str(datetime.date.today()), sleep, water, walk, 0, 0))
            conn.commit()
            st.success("Health logged!")

# --- L2: LEARNING ---
with tabs[2]:
    st.markdown("### Add Learning Debt")
    with st.form("learning_form"):
        topic = st.text_input("Topic (e.g. Window Functions)")
        col1, col2, col3 = st.columns(3)
        diff = col1.slider("Difficulty", 1, 10, 5)
        imp = col2.slider("Importance", 1, 10, 5)
        freq = col3.slider("Interview Freq", 1, 10, 5)
        if st.form_submit_button("Add Topic"):
            conn.execute("INSERT INTO engine_learning_state (topic, difficulty, importance, interview_frequency, pipeline_stage) VALUES (?, ?, ?, ?, ?)", (topic, diff, imp, freq, "Learn"))
            conn.commit()
            st.success("Topic added!")

# --- L3: SESSIONS ---
with tabs[3]:
    st.markdown("### Log Deep Work Session")
    with st.form("session_form"):
        topic = st.text_input("Session Topic")
        dur = st.number_input("Duration (minutes)", min_value=1, value=60)
        outq = st.number_input("Output Quantity (Problems/Features completed)", min_value=0, value=1)
        if st.form_submit_button("Log Session"):
            conn.execute("INSERT INTO engine_sessions (date, topic, start_time, end_time, duration_minutes, output_quantity) VALUES (?, ?, ?, ?, ?, ?)", (str(datetime.date.today()), topic, "Started", "Ended", dur, outq))
            conn.commit()
            st.success("Session logged!")

# --- L4: ANALYTICS ---
with tabs[4]:
    st.markdown("### Deep Work Analytics")
    df = pd.read_sql_query("SELECT date, SUM(output_quantity) as total_output FROM engine_sessions GROUP BY date ORDER BY date", conn)
    if not df.empty:
        fig = px.bar(df, x="date", y="total_output", title="Output Velocity Over Time", template="plotly_dark", color_discrete_sequence=["#8b5cf6"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No session data yet.")

# --- L5: CAREER ---
with tabs[5]:
    st.markdown("### Log Career Output")
    with st.form("career_form"):
        desc = st.text_area("What did you do? (e.g. Built RAG chatbot)")
        if st.form_submit_button("Generate AI Resume Bullet & Log"):
            # Mock AI Transformer
            impact = f"Engineered scalable solutions for {desc} utilizing modern software architecture principles."
            if "rag" in desc.lower(): impact = "Developed a Retrieval-Augmented Generation system using vector embeddings for document question answering."
            conn.execute("INSERT INTO engine_career (date, category, description, resume_impact) VALUES (?, ?, ?, ?)", (str(datetime.date.today()), "Project Feature", desc, impact))
            conn.commit()
            st.success(f"Logged! Generated Impact: {impact}")
