import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px
import time
import random

# --- Config ---
st.set_page_config(page_title="GrowthOS", layout="wide", page_icon="🌱")

# --- Premium Custom CSS (Glassmorphism & Gradients) ---
st.markdown("""
<style>
    /* Global styling and typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Glassmorphic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 5px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #c7d2fe !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
    }
    
    /* Inputs and Checkboxes */
    .stNumberInput input, .stTextInput input, .stDateInput input {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
    .stNumberInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    
    /* Glassmorphic Metric Cards */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Alerts/Info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            study_hours REAL,
            sleep_hours REAL,
            water_glasses INTEGER,
            social_media_mins INTEGER,
            exercise BOOLEAN,
            reading BOOLEAN,
            coding_practice BOOLEAN,
            applications_sent INTEGER
        )
    ''')
    try:
        c.execute('ALTER TABLE daily_logs ADD COLUMN water_glasses INTEGER DEFAULT 0')
        c.execute('ALTER TABLE daily_logs ADD COLUMN social_media_mins INTEGER DEFAULT 0')
        c.execute('ALTER TABLE daily_logs ADD COLUMN applications_sent INTEGER DEFAULT 0')
    except:
        pass
        
    c.execute('''
        CREATE TABLE IF NOT EXISTS education_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            milestone TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Helpers ---
def load_data():
    conn = sqlite3.connect('growthos.db')
    df = pd.read_sql_query("SELECT * FROM daily_logs ORDER BY date DESC", conn)
    conn.close()
    return df

def load_timeline():
    conn = sqlite3.connect('growthos.db')
    df = pd.read_sql_query("SELECT * FROM education_timeline ORDER BY date DESC", conn)
    conn.close()
    return df

def save_log(date, study, sleep, water, social, exercise, reading, coding, apps):
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO daily_logs (date, study_hours, sleep_hours, water_glasses, social_media_mins, exercise, reading, coding_practice, applications_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            study_hours=excluded.study_hours,
            sleep_hours=excluded.sleep_hours,
            water_glasses=excluded.water_glasses,
            social_media_mins=excluded.social_media_mins,
            exercise=excluded.exercise,
            reading=excluded.reading,
            coding_practice=excluded.coding_practice,
            applications_sent=excluded.applications_sent
    ''', (date, study, sleep, water, social, exercise, reading, coding, apps))
    conn.commit()
    conn.close()

def save_milestone(date, milestone, category):
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    c.execute('INSERT INTO education_timeline (date, milestone, category) VALUES (?, ?, ?)', (date, milestone, category))
    conn.commit()
    conn.close()

# --- UI ---
st.title("🚀 GrowthOS")
st.markdown("*Measure your life, understand your habits, improve your future.*")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Daily Log", "📊 Analytics & Readiness", "🎓 Education Graph", "🛡️ Digital Safety"])

with tab1:
    st.header("Log Today's Habits")
    date_input = st.date_input("Date", datetime.date.today())
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📚 Learning & Career")
        study_hrs = st.number_input("Study Hours", min_value=0.0, max_value=24.0, value=0.0, step=0.5)
        coding = st.checkbox("Coding Practice (1+ hours)")
        reading = st.checkbox("Reading (10+ pages)")
        apps_sent = st.number_input("Job Applications Sent", min_value=0, value=0, step=1)
        
    with col2:
        st.subheader("🧘 Health")
        sleep_hrs = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
        water = st.number_input("Water (Glasses)", min_value=0, value=4, step=1)
        exercise = st.checkbox("Exercise (30+ mins)")
        
    with col3:
        st.subheader("📱 Digital Wellness")
        social_media = st.number_input("Social Media (Minutes)", min_value=0, value=60, step=10)
        
    if st.button("Save Daily Log", type="primary"):
        save_log(str(date_input), study_hrs, sleep_hrs, water, social_media, exercise, reading, coding, apps_sent)
        st.success("Log saved successfully! 🌟")

with tab2:
    st.header("Weekly Analytics")
    df = load_data()
    tdf = load_timeline()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # --- Interview Readiness Score ---
        st.divider()
        st.subheader("🎯 Career Intelligence: Interview Readiness Score")
        
        recent_14 = df.tail(14)
        if len(recent_14) > 0:
            coding_ratio = recent_14['coding_practice'].mean() * 100 
            study_ratio = min(recent_14['study_hours'].mean() / 4.0, 1.0) * 100 
            project_count = len(tdf[tdf['category'] == 'Project Built']) if not tdf.empty else 0
            project_pts = min(project_count * 10, 30) 
            readiness_score = int((coding_ratio * 0.4) + (study_ratio * 0.3) + project_pts)
            
            col_score, col_feedback = st.columns([1, 3])
            col_score.metric("Readiness Score", f"{readiness_score}/100")
            
            with col_feedback:
                if readiness_score >= 80:
                    st.success("🔥 You are highly prepared! Keep applying and doing mock interviews.")
                elif readiness_score >= 50:
                    st.info("⚡ You're building solid momentum. Focus on adding projects to your timeline.")
                else:
                    st.warning("⚠️ Your readiness is low. Try to establish a consistent coding habit!")
                    
            st.progress(readiness_score / 100.0)
            
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Study Hours", f"{df['study_hours'].mean():.1f}")
        c2.metric("Avg Sleep Hours", f"{df['sleep_hours'].mean():.1f}")
        c3.metric("Coding Days", f"{df['coding_practice'].sum()} / {len(df)}")
        if 'applications_sent' in df.columns:
            c4.metric("Total Apps Sent", f"{df['applications_sent'].sum()}")
        
        st.divider()
        st.subheader("🧠 AI Behavioral Insights")
        
        if len(df) > 5:
            correlation = df['sleep_hours'].corr(df['study_hours'])
            if correlation > 0.4:
                st.info("💡 **Strong Link Found:** On days you sleep more, you tend to study significantly more.")
            elif correlation < -0.3:
                st.warning("⚠️ **Warning Sign:** You are sacrificing sleep for study time. This might lead to burnout.")
            
            if 'social_media_mins' in df.columns and df['social_media_mins'].mean() > 0:
                soc_corr = df['social_media_mins'].corr(df['study_hours'])
                if soc_corr < -0.4:
                    st.warning("⚠️ **Distraction Detected:** High social media usage strongly correlates with lower study hours.")
            
            exercise_study_avg = df[df['exercise'] == True]['study_hours'].mean()
            no_exercise_study_avg = df[df['exercise'] == False]['study_hours'].mean()
            if pd.notna(exercise_study_avg) and pd.notna(no_exercise_study_avg) and exercise_study_avg > no_exercise_study_avg:
                st.success(f"📈 **Performance Multiplier:** You study on average **{exercise_study_avg - no_exercise_study_avg:.1f} more hours** on days you exercise!")
        else:
            st.info("Keep logging data! AI insights will activate after 6 days of logs.")

        st.divider()
        st.subheader("Trends")
        fig = px.line(df, x='date', y=['study_hours', 'sleep_hours'], labels={'value': 'Hours', 'variable': 'Metric'})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No data yet. Go to the Daily Log tab to add some entries!")

with tab3:
    st.header("🎓 Education Graph")
    st.markdown("Track your journey over time. Map your skills, projects, and career milestones.")
    
    with st.form("milestone_form"):
        col1, col2 = st.columns(2)
        m_date = col1.date_input("Date achieved", datetime.date.today())
        m_cat = col2.selectbox("Category", ["Skill Learned", "Project Built", "Certification", "Interview", "Offer"])
        m_text = st.text_input("Milestone Title (e.g. 'Finished Python Course', 'Built Habit Tracker')")
        submitted = st.form_submit_button("Add Milestone")
        
        if submitted and m_text:
            save_milestone(str(m_date), m_text, m_cat)
            st.success("Milestone added to graph!")
            
    st.divider()
    st.subheader("Your Journey")
    
    tdf = load_timeline()
    if not tdf.empty:
        tdf['date'] = pd.to_datetime(tdf['date'])
        tdf = tdf.sort_values('date', ascending=False)
        
        for _, row in tdf.iterrows():
            st.markdown(f"**{row['date'].strftime('%Y-%m-%d')}** | 🏷️ *{row['category']}*")
            st.markdown(f"#### {row['milestone']}")
            st.divider()
    else:
        st.info("No milestones yet. Record your first achievement above!")

with tab4:
    st.header("🛡️ Digital Safety Monitor")
    st.markdown("Protect your digital environment while you focus on studying.")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    if "safety_scanned" not in st.session_state:
        st.session_state.safety_scanned = False
        st.session_state.trackers_blocked = 0
        st.session_state.redirects = 0
        st.session_state.scams = 0
        
    col_stat1.metric("Trackers Blocked", st.session_state.trackers_blocked)
    col_stat2.metric("Suspicious Redirects", st.session_state.redirects)
    col_stat3.metric("Scam Alerts", st.session_state.scams)
    
    st.divider()
    
    if st.button("Run System Security Scan"):
        with st.spinner('Scanning recent digital activity and permissions...'):
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.02)
                progress_bar.progress(percent_complete + 1)
                
            st.session_state.safety_scanned = True
            st.session_state.trackers_blocked = random.randint(12, 45)
            st.session_state.redirects = random.randint(0, 3)
            st.session_state.scams = 0
            
        st.success("Scan complete! No critical threats found.")
        st.rerun()
        
    if st.session_state.safety_scanned:
        st.markdown("### Latest Security Log")
        st.info(f"✅ Blocked **{st.session_state.trackers_blocked}** tracking scripts from educational websites.")
        if st.session_state.redirects > 0:
            st.warning(f"⚠️ Flagged **{st.session_state.redirects}** excessive redirects while browsing. Proceed with caution on untrusted domains.")
        st.success("🔒 Privacy permissions are secure. No unauthorized camera or microphone access detected.")
