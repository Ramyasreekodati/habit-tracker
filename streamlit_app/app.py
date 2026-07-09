import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(page_title="GrowthOS V11", layout="wide")

API_URL = "http://localhost:8000"

st.title("Ikigai 生き甲斐")
st.caption("Mission: Become an AI Engineer.")

today = date.today().isoformat()

@st.cache_data(ttl=2)
def get_habits():
    try:
        return requests.get(f"{API_URL}/habits/").json()
    except:
        return []

@st.cache_data(ttl=2)
def get_habit_logs():
    try:
        return requests.get(f"{API_URL}/habit_logs/").json()
    except:
        return []

@st.cache_data(ttl=2)
def get_hansei():
    try:
        return requests.get(f"{API_URL}/hansei/").json()
    except:
        return []

habits = get_habits()
logs = get_habit_logs()
hansei = get_hansei()

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Analytics", "Hansei", "AI Coach"])

with tab1:
    st.header("Today's Kaizen")
    categories = ['Career', 'MBA', 'Discipline', 'Bad Habits']
    
    # Filter logs for today
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
                    requests.post(f"{API_URL}/habit_logs/", json={
                        "habit_id": h['id'],
                        "date": today,
                        "completed": completed,
                        "duration": duration
                    })
                    st.rerun()

with tab2:
    st.header("Analytics")
    if not logs:
        st.info("No data yet.")
    else:
        # Study Hours Pie Chart
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
            # compute score over last 7 days
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
            requests.post(f"{API_URL}/hansei/", json={
                "date": today,
                "finished": f1,
                "distracted": f2,
                "mistake": f3,
                "change_tomorrow": f4
            })
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
                res = requests.get(f"{API_URL}/ai/analyze").json()
                st.subheader("Detected Patterns")
                for p in res.get("patterns", []): st.write(f"- {p}")
                st.subheader("Burnout & Risks")
                for p in res.get("risks", []): st.write(f"- {p}")
                st.subheader("Recommendations")
                for p in res.get("recommendations", []): st.write(f"- {p}")
            except Exception as e:
                st.error("Could not fetch insights. Make sure FastAPI is running!")
