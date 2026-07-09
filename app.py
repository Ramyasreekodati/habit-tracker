import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ---------------------------------------------------------
# DATABASE CONFIGURATION (V1.0)
# ---------------------------------------------------------
engine = create_engine("sqlite:///growthos.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    default_planned_time = Column(Integer, default=0) # in minutes

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    date = Column(String, index=True)
    completed = Column(Boolean, default=False)
    planned_duration = Column(Integer, default=0)
    duration = Column(Integer, default=0) # actual time
    time_of_day = Column(String) # Morning, Afternoon, Night
    friction_reason = Column(String) # Too difficult, Too boring, Too large, Distracted, Didn't know next step
    habit = relationship("Habit")

class EnergyLog(Base):
    __tablename__ = "energy_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    morning_energy = Column(String, default="Medium")
    afternoon_energy = Column(String, default="Medium")
    night_energy = Column(String, default="Medium")

class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    category = Column(String)
    progress = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    if db.query(Habit).count() == 0:
        default_habits = [
            {"name": "Python", "category": "AI Core", "default_planned_time": 120},
            {"name": "SQL", "category": "AI Core", "default_planned_time": 60},
            {"name": "DSA", "category": "AI Core", "default_planned_time": 60},
            {"name": "GenAI Projects", "category": "AI Core", "default_planned_time": 120},
            {"name": "MBA Assignment", "category": "MBA", "default_planned_time": 120},
            {"name": "Classes", "category": "MBA", "default_planned_time": 180},
            {"name": "Meditation", "category": "Discipline", "default_planned_time": 0},
            {"name": "Exercise", "category": "Discipline", "default_planned_time": 0}
        ]
        for h in default_habits:
            db.add(Habit(**h))
        
        roadmap_items = [
            {"topic": "Python Basics", "category": "Foundations", "progress": 100},
            {"topic": "Pandas/NumPy", "category": "Foundations", "progress": 80},
            {"topic": "SQL Window Functions", "category": "Foundations", "progress": 70},
            {"topic": "Machine Learning", "category": "AI Core", "progress": 40},
            {"topic": "Deep Learning", "category": "AI Core", "progress": 10},
            {"topic": "Transformers", "category": "GenAI", "progress": 20},
            {"topic": "RAG", "category": "GenAI", "progress": 10}
        ]
        for r in roadmap_items:
            db.add(RoadmapItem(**r))
            
        db.commit()
    db.close()

seed_db()

# ---------------------------------------------------------
# UI CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="GrowthOS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 600; }
    .metric-card { background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; text-align: center; margin-bottom: 15px;}
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #2ea043; }
    .metric-label { font-size: 0.9rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

today = date.today().isoformat()

# Fetch Data Functions
def get_db():
    return SessionLocal()

db = get_db()
habits = db.query(Habit).all()
logs_today = db.query(HabitLog).filter(HabitLog.date == today).all()
energy_today = db.query(EnergyLog).filter(EnergyLog.date == today).first()
if not energy_today:
    energy_today = EnergyLog(date=today)
    db.add(energy_today)
    db.commit()
    
# Initialize today's logs if they don't exist
log_dict = {l.habit_id: l for l in logs_today}
for h in habits:
    if h.id not in log_dict:
        new_log = HabitLog(habit_id=h.id, date=today, planned_duration=h.default_planned_time)
        db.add(new_log)
        log_dict[h.id] = new_log
db.commit()

# Sidebar Navigation
st.sidebar.title("GrowthOS")
st.sidebar.caption("AI Engineer Operating System")
nav = st.sidebar.radio("Navigation", ["📝 Daily Log", "📊 Analytics Dashboard", "🔄 Weekly Review", "🗺️ Roadmap Tracker"])

# ---------------------------------------------------------
# PAGE 1: DAILY LOG
# ---------------------------------------------------------
if nav == "📝 Daily Log":
    st.title("Today's Execution")
    
    col1, col2, col3 = st.columns(3)
    
    # 1. Energy Tracker
    with st.expander("⚡ Daily Energy Tracker", expanded=True):
        ec1, ec2, ec3 = st.columns(3)
        morning = ec1.selectbox("Morning", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(energy_today.morning_energy))
        afternoon = ec2.selectbox("Afternoon", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(energy_today.afternoon_energy))
        night = ec3.selectbox("Night", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(energy_today.night_energy))
        if morning != energy_today.morning_energy or afternoon != energy_today.afternoon_energy or night != energy_today.night_energy:
            energy_today.morning_energy = morning
            energy_today.afternoon_energy = afternoon
            energy_today.night_energy = night
            db.commit()

    # 2. Daily Grid
    st.markdown("### Core Tasks")
    
    for h in habits:
        l = log_dict[h.id]
        
        c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 2])
        
        completed = c1.checkbox(f"{h.name} ({h.category})", value=l.completed, key=f"chk_{h.id}")
        
        if h.category in ["AI Core", "MBA"]:
            planned = c2.number_input("Plan (m)", value=l.planned_duration, key=f"plan_{h.id}", label_visibility="collapsed")
            actual = c3.number_input("Act (m)", value=l.duration, key=f"act_{h.id}", label_visibility="collapsed")
            tod = c4.selectbox("Time", ["Morning", "Afternoon", "Night"], index=0 if not l.time_of_day else ["Morning", "Afternoon", "Night"].index(l.time_of_day), key=f"tod_{h.id}", label_visibility="collapsed")
        else:
            planned = 0
            actual = 0
            tod = "Morning"
            c2.write("-")
            c3.write("-")
            c4.write("-")
            
        friction = c5.selectbox("Reason for Failure", ["-", "Too difficult", "Too boring", "Too large", "Distracted", "No clear next step"], index=0 if not l.friction_reason else ["-", "Too difficult", "Too boring", "Too large", "Distracted", "No clear next step"].index(l.friction_reason), key=f"fric_{h.id}", label_visibility="collapsed")
        
        if completed != l.completed or planned != l.planned_duration or actual != l.duration or tod != l.time_of_day or friction != l.friction_reason:
            l.completed = completed
            l.planned_duration = planned
            l.duration = actual
            l.time_of_day = tod
            l.friction_reason = friction if not completed and friction != "-" else None
            db.commit()

# ---------------------------------------------------------
# PAGE 2: ANALYTICS DASHBOARD
# ---------------------------------------------------------
elif nav == "📊 Analytics Dashboard":
    st.title("Performance Analytics")
    
    all_logs = db.query(HabitLog).all()
    if not all_logs:
        st.warning("No data available.")
    else:
        df = pd.DataFrame([{"date": l.date, "completed": l.completed, "planned": l.planned_duration, "actual": l.duration, "time_of_day": l.time_of_day, "friction": l.friction_reason, "cat": l.habit.category} for l in all_logs])
        
        # Calculate Focus Score (Actual / Planned * 100)
        core_tasks = df[df['cat'].isin(['AI Core', 'MBA'])]
        planned_total = core_tasks['planned'].sum()
        actual_total = core_tasks['actual'].sum()
        focus_score = (actual_total / planned_total * 100) if planned_total > 0 else 0
        
        # Calculate Completion Ratio
        completion_ratio = (df['completed'].sum() / len(df)) * 100 if len(df) > 0 else 0
        
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><div class="metric-value">{int(focus_score)}%</div><div class="metric-label">Focus Score</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-value">{int(completion_ratio)}%</div><div class="metric-label">Task Completion Ratio</div></div>', unsafe_allow_html=True)
        
        st.markdown("### Deep Work Heatmap")
        st.caption("When are you most productive? (Total Actual Mins)")
        # Heatmap based on time_of_day
        hm_data = core_tasks.groupby('time_of_day')['actual'].sum().reset_index()
        # Sort Morning, Afternoon, Night
        hm_data['time_of_day'] = pd.Categorical(hm_data['time_of_day'], categories=["Morning", "Afternoon", "Night"], ordered=True)
        hm_data = hm_data.sort_values('time_of_day')
        
        if not hm_data.empty:
            fig = px.bar(hm_data, x="time_of_day", y="actual", color="time_of_day", color_discrete_sequence=['#2ea043', '#1f6feb', '#d29922'])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PAGE 3: WEEKLY REVIEW
# ---------------------------------------------------------
elif nav == "🔄 Weekly Review":
    st.title("Weekly Review & Mistake Analysis")
    
    last_7_days = [(date.today() - timedelta(days=i)).isoformat() for i in range(7)]
    weekly_logs = db.query(HabitLog).filter(HabitLog.date.in_(last_7_days)).all()
    
    df_w = pd.DataFrame([{"planned": l.planned_duration, "actual": l.duration, "friction": l.friction_reason, "cat": l.habit.category} for l in weekly_logs if l.habit.category in ['AI Core', 'MBA']])
    
    if not df_w.empty:
        planned_hrs = df_w['planned'].sum() / 60
        actual_hrs = df_w['actual'].sum() / 60
        lost_hrs = planned_hrs - actual_hrs
        if lost_hrs < 0: lost_hrs = 0
        
        st.markdown("### Time Leakage (Sankey Diagram)")
        st.caption("Where did your planned deep work time go?")
        
        # Build Sankey: Planned (0) -> Actual (1), Lost (2)
        # Lost (2) -> Too difficult (3), Distracted (4), etc.
        
        friction_counts = df_w[df_w['friction'].notnull()]['friction'].value_counts()
        
        # Nodes
        node_labels = ["Planned Time", "Actual Output", "Lost Time"] + list(friction_counts.index)
        
        source = [0, 0]
        target = [1, 2]
        value = [actual_hrs, lost_hrs]
        
        for i, (reason, count) in enumerate(friction_counts.items()):
            source.append(2)
            target.append(3 + i)
            # Estimate hours lost per friction reason (proportional)
            value.append(lost_hrs * (count / friction_counts.sum()) if friction_counts.sum() > 0 else 0)
            
        fig_sankey = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 15,
              thickness = 20,
              line = dict(color = "black", width = 0.5),
              label = node_labels,
              color = ["#8b949e", "#2ea043", "#f85149"] + ["#d29922"] * len(friction_counts)
            ),
            link = dict(
              source = source,
              target = target,
              value = value
          ))])
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        st.markdown("### Friction Analysis")
        st.caption("Why are tasks failing?")
        if not friction_counts.empty:
            fig_fric = px.bar(x=friction_counts.index, y=friction_counts.values, labels={'x':'Reason', 'y':'Failed Tasks'}, color_discrete_sequence=['#f85149'])
            fig_fric.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_fric, use_container_width=True)
        else:
            st.success("No friction reasons logged this week. Excellent discipline!")
    else:
        st.info("No deep work data logged for the past 7 days.")

# ---------------------------------------------------------
# PAGE 4: ROADMAP TRACKER
# ---------------------------------------------------------
elif nav == "🗺️ Roadmap Tracker":
    st.title("AI Engineer & MBA Roadmap")
    
    roadmaps = db.query(RoadmapItem).all()
    categories = list(set([r.category for r in roadmaps]))
    
    for cat in categories:
        st.markdown(f"### {cat}")
        items = [r for r in roadmaps if r.category == cat]
        for i in items:
            st.markdown(f"**{i.topic}**")
            st.progress(i.progress / 100, text=f"{i.progress}% Complete")

db.close()
