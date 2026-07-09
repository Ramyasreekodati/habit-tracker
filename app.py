import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import os
import json
import calendar
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from openai import OpenAI

# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------
engine = create_engine("sqlite:///growthos.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    date = Column(String, index=True)
    completed = Column(Boolean, default=False)
    duration = Column(Integer, default=0)
    habit = relationship("Habit")

class HanseiReflection(Base):
    __tablename__ = "hansei_reflections"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    finished = Column(String)
    distracted = Column(String)
    mistake = Column(String)
    change_tomorrow = Column(String)

Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    if db.query(Habit).count() == 0:
        default_habits = [
            {"name": "Python", "category": "Career"},
            {"name": "SQL", "category": "Career"},
            {"name": "DSA", "category": "Career"},
            {"name": "GenAI", "category": "Career"},
            {"name": "Project Work", "category": "Career"},
            {"name": "Classes", "category": "MBA"},
            {"name": "Assignments", "category": "MBA"},
            {"name": "Meditation", "category": "Discipline"},
            {"name": "Housework", "category": "Discipline"},
            {"name": "Sleep", "category": "Discipline"},
            {"name": "Exercise", "category": "Discipline"},
            {"name": "Phone overuse", "category": "Bad Habits"},
            {"name": "Procrastination", "category": "Bad Habits"},
            {"name": "Overthinking", "category": "Bad Habits"},
            {"name": "Late sleeping", "category": "Bad Habits"}
        ]
        for h in default_habits:
            db.add(Habit(**h))
        db.commit()
    db.close()

seed_db()

# ---------------------------------------------------------
# UI CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="GrowthOS V11", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Premium aesthetics */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom-color: #00FFAA !important; color: #00FFAA !important; }
    .metric-card { background: #161B22; padding: 20px; border-radius: 12px; border: 1px solid #30363D; text-align: center; }
    .metric-value { font-size: 2rem; font-weight: bold; color: #00FFAA; }
    .metric-label { font-size: 0.9rem; color: #8B949E; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

st.title("GrowthOS 生き甲斐")
st.caption("A system for extreme personal accountability.")

today = date.today().isoformat()

def get_habits():
    db = SessionLocal()
    habits = db.query(Habit).all()
    res = [{"id": h.id, "name": h.name, "category": h.category} for h in habits]
    db.close()
    return res

def get_habit_logs():
    db = SessionLocal()
    logs = db.query(HabitLog).all()
    res = [{"id": l.id, "habit_id": l.habit_id, "date": l.date, "completed": l.completed, "duration": l.duration} for l in logs]
    db.close()
    return res

def get_hansei():
    db = SessionLocal()
    reflections = db.query(HanseiReflection).all()
    res = [{"id": r.id, "date": r.date, "finished": r.finished, "distracted": r.distracted, "mistake": r.mistake, "change_tomorrow": r.change_tomorrow} for r in reflections]
    db.close()
    return res

def save_log(habit_id, completed, duration):
    db = SessionLocal()
    log = db.query(HabitLog).filter(HabitLog.habit_id == habit_id, HabitLog.date == today).first()
    if log:
        log.completed = completed
        log.duration = duration
    else:
        log = HabitLog(habit_id=habit_id, date=today, completed=completed, duration=duration)
        db.add(log)
    db.commit()
    db.close()

habits = get_habits()
logs = get_habit_logs()
hansei = get_hansei()

tab1, tab2, tab3, tab4 = st.tabs(["📌 Daily Kaizen", "📅 Monthly View", "🗺️ Yearly Heatmap", "🤖 AI Coach"])

# ---------------------------------------------------------
# L1: DAILY KAIZEN
# ---------------------------------------------------------
with tab1:
    st.markdown("### Today's Action Plan")
    categories = ['Career', 'MBA', 'Discipline', 'Bad Habits']
    today_logs_dict = {l['habit_id']: l for l in logs if l['date'] == today}
    
    # Calculate daily progress
    total_good_habits = len([h for h in habits if h['category'] != 'Bad Habits'])
    completed_good = len([l for l in today_logs_dict.values() if l['completed'] and next((h for h in habits if h['id'] == l['habit_id']), {}).get('category') != 'Bad Habits'])
    progress = completed_good / total_good_habits if total_good_habits > 0 else 0
    
    st.progress(progress, text=f"Daily Completion: {int(progress * 100)}%")
    st.write("---")
    
    col1, col2 = st.columns(2)
    for i, category in enumerate(categories):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"#### {category}")
            cat_habits = [h for h in habits if h['category'] == category]
            for h in cat_habits:
                h_log = today_logs_dict.get(h['id'], {'completed': False, 'duration': 0})
                
                cols = st.columns([3, 1])
                with cols[0]:
                    completed = st.checkbox(h['name'], value=h_log['completed'], key=f"chk_{h['id']}")
                with cols[1]:
                    if category in ['Career', 'MBA']:
                        duration = st.number_input("mins", value=h_log['duration'], step=10, key=f"dur_{h['id']}")
                    else:
                        duration = 0
                        
                if completed != h_log['completed'] or duration != h_log['duration']:
                    save_log(h['id'], completed, duration)
                    st.rerun()

# ---------------------------------------------------------
# L2: MONTHLY VIEW
# ---------------------------------------------------------
with tab2:
    st.markdown("### Monthly Performance Dashboard")
    
    # Filter logs for current month
    current_month_prefix = today[:7]
    monthly_logs = [l for l in logs if l['date'].startswith(current_month_prefix)]
    
    # Calculate stats
    total_study_mins = sum(l['duration'] for l in monthly_logs)
    days_logged = len(set(l['date'] for l in monthly_logs))
    
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div class="metric-value">{total_study_mins // 60}h {total_study_mins % 60}m</div><div class="metric-label">Deep Work Logged</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-value">{days_logged}</div><div class="metric-label">Active Days</div></div>', unsafe_allow_html=True)
    
    positive_logs = [l for l in monthly_logs if l['completed'] and next((h for h in habits if h['id'] == l['habit_id']), {}).get('category') != 'Bad Habits']
    m3.markdown(f'<div class="metric-card"><div class="metric-value">{len(positive_logs)}</div><div class="metric-label">Positive Actions</div></div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Monthly Trends Chart
    if monthly_logs:
        df_month = pd.DataFrame(monthly_logs)
        # merge with habits to get category
        habit_lookup = {h['id']: h['category'] for h in habits}
        df_month['category'] = df_month['habit_id'].map(habit_lookup)
        
        # Count completions per day
        df_trends = df_month[df_month['completed'] == True].groupby('date').size().reset_index(name='completions')
        
        fig = px.area(df_trends, x='date', y='completions', title="Daily Task Output (Current Month)", template="plotly_dark", color_discrete_sequence=['#00FFAA'])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# L3: YEARLY HEATMAP
# ---------------------------------------------------------
with tab3:
    st.markdown("### 12-Month Consistency Heatmap")
    
    if logs:
        # Prepare data for 365 days
        end_date = date.today()
        start_date = end_date - timedelta(days=364)
        
        # Create full date range
        all_dates = [start_date + timedelta(days=x) for x in range(365)]
        date_strs = [d.isoformat() for d in all_dates]
        
        # Calculate daily scores
        score_map = {}
        df_logs = pd.DataFrame(logs)
        if not df_logs.empty:
            habit_lookup = {h['id']: h['category'] for h in habits}
            df_logs['category'] = df_logs['habit_id'].map(habit_lookup)
            # good habits completed
            good_logs = df_logs[(df_logs['completed'] == True) & (df_logs['category'] != 'Bad Habits')]
            daily_scores = good_logs.groupby('date').size().to_dict()
            for d in date_strs:
                score_map[d] = daily_scores.get(d, 0)
        
        # Build heatmap matrix (7 rows for days of week, 52 cols for weeks)
        z = np.zeros((7, 53))
        text = np.empty((7, 53), dtype=object)
        
        # We start filling from the day of week of start_date
        start_dow = start_date.weekday() # 0 = Mon, 6 = Sun
        
        for i, d in enumerate(all_dates):
            week = (i + start_dow) // 7
            day = (i + start_dow) % 7
            val = score_map.get(d.isoformat(), 0)
            z[day, week] = val
            text[day, week] = f"{d.isoformat()}: {val} tasks"
            
        fig_heat = go.Figure(data=go.Heatmap(
            z=z,
            text=text,
            hoverinfo="text",
            colorscale=[[0, '#161B22'], [0.2, '#0e4429'], [0.4, '#006d32'], [0.6, '#26a641'], [1.0, '#39d353']],
            showscale=False,
            xgap=3,
            ygap=3
        ))
        
        fig_heat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=250,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, tickmode='array', tickvals=[0,2,4,6], ticktext=['Mon','Wed','Fri','Sun'], autorange="reversed")
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Log some habits to see your yearly consistency heatmap!")

# ---------------------------------------------------------
# L4: AI COACH
# ---------------------------------------------------------
with tab4:
    st.markdown("### AI Coach & Reflection")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### Evening Reflection (Hansei)")
        today_hansei = next((x for x in hansei if x['date'] == today), {"finished": "", "distracted": "", "mistake": "", "change_tomorrow": ""})
        
        with st.form("hansei_form"):
            f1 = st.text_area("1. What did I finish today?", value=today_hansei['finished'])
            f2 = st.text_area("2. What distracted me today?", value=today_hansei['distracted'])
            f3 = st.text_area("3. What mistake did I repeat?", value=today_hansei['distracted']) # using mistake logic
            f4 = st.text_area("4. What will I change tomorrow?", value=today_hansei['change_tomorrow'])
            
            if st.form_submit_button("Save Reflection"):
                db = SessionLocal()
                r = db.query(HanseiReflection).filter(HanseiReflection.date == today).first()
                if r:
                    r.finished = f1
                    r.distracted = f2
                    r.mistake = f3
                    r.change_tomorrow = f4
                else:
                    r = HanseiReflection(date=today, finished=f1, distracted=f2, mistake=f3, change_tomorrow=f4)
                    db.add(r)
                db.commit()
                db.close()
                st.success("Saved!")
                st.rerun()

    with c2:
        st.markdown("#### AI Insights")
        if st.button("Generate Strategic Insights"):
            with st.spinner("Analyzing your logs and reflections..."):
                try:
                    api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
                    
                    if not api_key or api_key == "your_openai_api_key_here":
                        st.warning("No OPENAI_API_KEY found in Streamlit Secrets. Showing mock insights.")
                        st.markdown("> **Pattern:** You are most productive when you sleep 8 hours.\n\n> **Risk:** High chance of burnout this week due to consecutive overworking.\n\n> **Action:** Disconnect at 9 PM tonight.")
                    else:
                        client = OpenAI(api_key=api_key)
                        data_summary = f"Total logs: {len(logs)}, Total reflections: {len(hansei)}\n"
                        for r in hansei[-3:]:
                            data_summary += f"Date: {r['date']}\nFinished: {r['finished']}\nDistracted: {r['distracted']}\nMistake: {r['mistake']}\nChange: {r['change_tomorrow']}\n"
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are an elite productivity AI. Analyze this habit data and return actionable, hard-hitting advice."},
                                {"role": "user", "content": f"Analyze this recent habit data:\n{data_summary}"}
                            ]
                        )
                        st.info(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error connecting to AI: {e}")
