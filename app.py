import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from openai import OpenAI

# ---------------------------------------------------------
# DATABASE CONFIGURATION (STANDALONE FOR STREAMLIT CLOUD)
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
# UI CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="GrowthOS V11", layout="wide")
st.title("Ikigai 生き甲斐")
st.caption("Mission: Become an AI Engineer.")

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

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Analytics", "Hansei", "AI Coach"])

with tab1:
    st.header("Today's Kaizen")
    categories = ['Career', 'MBA', 'Discipline', 'Bad Habits']
    
    today_logs_dict = {l['habit_id']: l for l in logs if l['date'] == today}
    
    col1, col2 = st.columns(2)
    for i, category in enumerate(categories):
        with (col1 if i % 2 == 0 else col2):
            st.subheader(category)
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

with tab2:
    st.header("Analytics")
    if not logs:
        st.info("No data yet.")
    else:
        study_data = []
        for l in logs:
            h = next((x for x in habits if x['id'] == l['habit_id']), None)
            if h and h['category'] in ['Career', 'MBA'] and l['duration'] > 0:
                study_data.append({"Subject": h['name'], "Minutes": l['duration']})
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Study Hours Distribution")
            if study_data:
                df_study = pd.DataFrame(study_data).groupby("Subject").sum().reset_index()
                fig1 = px.pie(df_study, values="Minutes", names="Subject", hole=0.4)
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.write("No study hours logged.")
                
        with col2:
            st.subheader("Daily Completion Rate")
            comp_data = []
            for i in range(6, -1, -1):
                d = (date.today() - timedelta(days=i)).isoformat()
                day_logs = [l for l in logs if l['date'] == d and l['completed']]
                pos_logs = [l for l in day_logs if next((x for x in habits if x['id'] == l['habit_id']), {}).get('category') != 'Bad Habits']
                tot_pos = len([h for h in habits if h['category'] != 'Bad Habits']) or 1
                comp_data.append({"Date": d, "Score": round((len(pos_logs)/tot_pos)*100)})
                
            df_comp = pd.DataFrame(comp_data)
            fig2 = px.bar(df_comp, x="Date", y="Score", range_y=[0, 100])
            st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.header("Hansei Reflection 反省")
    today_hansei = next((x for x in hansei if x['date'] == today), {"finished": "", "distracted": "", "mistake": "", "change_tomorrow": ""})
    
    with st.form("hansei_form"):
        f1 = st.text_area("1. What did I finish today?", value=today_hansei['finished'])
        f2 = st.text_area("2. What distracted me today?", value=today_hansei['distracted'])
        f3 = st.text_area("3. What mistake did I repeat?", value=today_hansei['mistake'])
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
            
    st.subheader("Reflection History")
    for r in hansei:
        with st.expander(r['date']):
            st.write(f"**Finished:** {r['finished']}")
            st.write(f"**Distracted:** {r['distracted']}")
            st.write(f"**Mistake:** {r['mistake']}")
            st.write(f"**Change:** {r['change_tomorrow']}")

with tab4:
    st.header("AI Coach 知能")
    if st.button("Generate AI Insights"):
        with st.spinner("Analyzing..."):
            try:
                # Try getting the API key from Streamlit secrets (cloud) or OS env (local)
                api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
                
                if not api_key or api_key == "your_openai_api_key_here":
                    st.warning("No OPENAI_API_KEY found in Streamlit Secrets. Showing mock data.")
                    st.subheader("Detected Patterns")
                    st.write("- You complete Python 90% of the time.")
                    st.subheader("Burnout & Risks")
                    st.write("- Your sleep has dropped below 6 hours.")
                    st.subheader("Recommendations")
                    st.write("- Move DSA to morning hours.")
                else:
                    client = OpenAI(api_key=api_key)
                    data_summary = f"Total logs: {len(logs)}, Total reflections: {len(hansei)}\n"
                    for r in hansei[-3:]:
                        data_summary += f"Date: {r['date']}\nFinished: {r['finished']}\nDistracted: {r['distracted']}\nMistake: {r['mistake']}\nChange: {r['change_tomorrow']}\n"
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a productivity AI coach analyzing a user's habits. Return ONLY JSON with three keys: 'patterns' (list of strings), 'risks' (list of strings), 'recommendations' (list of strings)."},
                            {"role": "user", "content": f"Analyze this recent habit and reflection data:\n{data_summary}"}
                        ]
                    )
                    content = response.choices[0].message.content
                    ai_data = json.loads(content)
                    
                    st.subheader("Detected Patterns")
                    for p in ai_data.get("patterns", []): st.write(f"- {p}")
                    st.subheader("Burnout & Risks")
                    for p in ai_data.get("risks", []): st.write(f"- {p}")
                    st.subheader("Recommendations")
                    for p in ai_data.get("recommendations", []): st.write(f"- {p}")
            except Exception as e:
                st.error(f"Error connecting to OpenAI: {e}")
