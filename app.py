import streamlit as st
import pandas as pd
import sqlite3
import datetime

st.set_page_config(page_title="GrowthOS Engine", layout="centered", page_icon="⚡")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #e2e8f0 !important; font-weight: 800 !important; }
    .next-task-box { background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-left: 5px solid #6366f1; border-radius: 8px; padding: 25px; margin-bottom: 30px; }
    .next-task-box h2 { margin-top: 0; color: #c7d2fe !important; }
    .metric-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .stButton > button { background-color: #6366f1 !important; color: white !important; border: none !important; width: 100%; border-radius: 6px !important; font-weight: 600 !important; padding: 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- Database ---
def init_db():
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS engine_health (date TEXT UNIQUE, sleep REAL, water INT, walk INT, exercise INT, meditation INT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS engine_career (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, description TEXT, resume_impact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS engine_learning_debt (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, status TEXT)''')
    # Seed learning debt if empty
    c.execute("SELECT COUNT(*) FROM engine_learning_debt")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO engine_learning_debt (topic, status) VALUES (?, ?)", 
                      [('SQL Window Functions', '❌ Not Mastered'), ('GenAI Embeddings', '✅ Mastered'), ('Python Pandas', '❌ Not Mastered')])
    conn.commit()
    conn.close()

init_db()

def execute_query(query, params=()):
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def load_df(query):
    conn = sqlite3.connect('growthos.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- Minimalist UI ---
tab_home, tab_health, tab_learning, tab_career = st.tabs(["⚡ What's Next?", "🧘 Health (L1)", "🧠 Learning (L2)", "🚀 Career (L3)"])

with tab_home:
    st.markdown("<div class='next-task-box'><h2>Current Task: SQL Window Functions</h2><p><b>Expected Duration:</b> 45 minutes</p><p><b>Reason:</b> This is your weakest interview area based on current Learning Debt.</p><p><b>Career Impact:</b> High | <b>Resume Impact:</b> Medium | <b>Difficulty:</b> High</p></div>", unsafe_allow_html=True)
    
    if st.button("✅ Mark Complete & Get Next Task"):
        st.success("Task Completed! Next Task Queued: GenAI RAG Implementation.")
        
    st.divider()
    st.subheader("Opportunity Cost Indicator")
    st.info("💡 If you spend 2 hours on YouTube right now, you will lose the opportunity to complete 1 Project Feature or solve 8 SQL problems.")

with tab_health:
    st.header("Layer 1: Fixed Health System")
    date_input = st.date_input("Date", datetime.date.today())
    c1, c2, c3 = st.columns(3)
    sleep = c1.number_input("Sleep (hrs)", 0.0, 24.0, 7.0)
    water = c2.number_input("Water (glasses)", 0, 20, 9)
    walk = c3.number_input("Walk (mins)", 0, 300, 45)
    
    if st.button("Log Health"):
        execute_query("INSERT INTO engine_health (date, sleep, water, walk, exercise, meditation) VALUES (?,?,?,0,0) ON CONFLICT(date) DO UPDATE SET sleep=excluded.sleep, water=excluded.water, walk=excluded.walk", (str(date_input), sleep, water, walk))
        st.success("Health logged.")
        
    df_h = load_df("SELECT * FROM engine_health ORDER BY date DESC LIMIT 7")
    if not df_h.empty:
        avg_sleep = df_h['sleep'].mean()
        if avg_sleep < 6.5:
            st.error(f"🚨 Recovery Warning: Sleep average is {avg_sleep:.1f}h. Recommendation: Reduce workload temporarily.")
        else:
            st.success(f"✅ Recovery Optimal: Sleep average is {avg_sleep:.1f}h.")

with tab_learning:
    st.header("Layer 2: Adaptive Learning System")
    st.subheader("Learning Debt")
    df_debt = load_df("SELECT * FROM engine_learning_debt")
    for _, row in df_debt.iterrows():
        st.markdown(f"**{row['status']}** | {row['topic']}")
        
    with st.form("add_debt"):
        t = st.text_input("New Topic")
        if st.form_submit_button("Add to Debt List"):
            execute_query("INSERT INTO engine_learning_debt (topic, status) VALUES (?, ?)", (t, "❌ Not Mastered"))
            st.rerun()

with tab_career:
    st.header("Layer 3: Output & Career System")
    st.subheader("Log Output & Resume Impact")
    with st.form("career_log"):
        cat = st.selectbox("Category", ["Project Feature", "Git Commit", "DSA Problem", "SQL Problem", "Application"])
        desc = st.text_input("Description (What did you do?)")
        impact = st.text_area("Resume Impact (How does this translate to a resume bullet?)")
        if st.form_submit_button("Log Output"):
            execute_query("INSERT INTO engine_career (date, category, description, resume_impact) VALUES (?,?,?,?)", (str(datetime.date.today()), cat, desc, impact))
            st.success("Output logged and mapped to resume!")
            
    st.divider()
    st.subheader("Momentum Tracker (Last 30 Days)")
    df_c = load_df("SELECT category, COUNT(*) as count FROM engine_career GROUP BY category")
    if not df_c.empty:
        cols = st.columns(len(df_c))
        for i, row in df_c.iterrows():
            cols[i].metric(row['category'], row['count'])
    else:
        st.write("No outputs logged yet.")
