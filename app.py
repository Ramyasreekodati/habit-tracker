import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import calendar
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ---------------------------------------------------------
# DATABASE CONFIGURATION (Google Sheets Style Grid)
# ---------------------------------------------------------
engine = create_engine("sqlite:///growthos.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    date = Column(String, index=True) # ISO format: YYYY-MM-DD
    completed = Column(Boolean, default=False)
    habit = relationship("Habit")

Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    if db.query(Habit).count() == 0:
        default_habits = [
            "Wake up 6 AM",
            "Drink Water",
            "Read 10 pages",
            "Exercise (30m)",
            "Python Study (1h)",
            "SQL Study (1h)",
            "Meditate",
            "No Phone in Bed"
        ]
        for h in default_habits:
            db.add(Habit(name=h))
        db.commit()
    db.close()

seed_db()

# ---------------------------------------------------------
# UI CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="Spreadsheet Habit Tracker", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #202124; }
    h1, h2, h3 { font-family: 'Arial', sans-serif; font-weight: bold; color: #1f1f1f; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3); text-align: center; margin-bottom: 20px; }
    .card-value { font-size: 2rem; font-weight: bold; color: #1a73e8; }
    .card-label { font-size: 0.9rem; color: #5f6368; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Personal Habit Tracker (Grid Dashboard)")
st.caption("A pure, spreadsheet-style dashboard based on classic Google Sheets tutorials.")

db = SessionLocal()
habits = db.query(Habit).all()

# Determine Current Month
today = date.today()
year, month = today.year, today.month
num_days = calendar.monthrange(year, month)[1]
month_name = calendar.month_name[month]

st.markdown(f"### 🗓️ {month_name} {year} Tracker")

# ---------------------------------------------------------
# SPREADSHEET GRID
# ---------------------------------------------------------
# Fetch logs for current month
month_prefix = f"{year}-{month:02d}-"
logs = db.query(HabitLog).filter(HabitLog.date.startswith(month_prefix)).all()

# Build DataFrame for Grid
# Index: Habit Name
# Columns: Day 1, Day 2 ... Day N
days = [str(d) for d in range(1, num_days + 1)]
df_data = {}
for h in habits:
    df_data[h.name] = {str(d): False for d in range(1, num_days + 1)}

for l in logs:
    day_str = str(int(l.date[-2:]))
    df_data[l.habit.name][day_str] = l.completed

df = pd.DataFrame.from_dict(df_data, orient='index')
# Reorder columns to ensure 1 to num_days
df = df[days]

# Render Interactive Data Editor
st.markdown("Check off your daily tasks below. The data saves automatically.")
edited_df = st.data_editor(
    df,
    use_container_width=True,
    height=350,
    column_config={d: st.column_config.CheckboxColumn(d, default=False) for d in days}
)

# Detect Changes and Save to DB
for h in habits:
    for d in range(1, num_days + 1):
        day_str = str(d)
        is_checked = edited_df.loc[h.name, day_str]
        was_checked = df.loc[h.name, day_str]
        
        if is_checked != was_checked:
            date_str = f"{year}-{month:02d}-{d:02d}"
            log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.date == date_str).first()
            if log:
                log.completed = bool(is_checked)
            else:
                log = HabitLog(habit_id=h.id, date=date_str, completed=bool(is_checked))
                db.add(log)
            db.commit()

# ---------------------------------------------------------
# ANALYSIS CHARTS
# ---------------------------------------------------------
st.write("---")
st.markdown("### 📈 Daily & Monthly Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**Daily Completion Rate (%)**")
    # Calculate column sums / total habits
    daily_sums = edited_df.sum(axis=0)
    daily_pct = (daily_sums / len(habits)) * 100
    df_daily = pd.DataFrame({"Day": days, "Completion %": daily_pct.values})
    
    fig_bar = px.bar(df_daily, x="Day", y="Completion %", text_auto='.0f', color="Completion %", color_continuous_scale="Blues")
    fig_bar.update_layout(xaxis_title="Day of Month", yaxis_title="%", yaxis=dict(range=[0, 100]), margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("**Overall Monthly Progress**")
    total_possible = len(habits) * num_days
    total_completed = edited_df.sum().sum()
    monthly_pct = (total_completed / total_possible) * 100 if total_possible > 0 else 0
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=['Completed', 'Remaining'], 
        values=[total_completed, total_possible - total_completed], 
        hole=.7,
        marker_colors=['#1a73e8', '#e8eaed']
    )])
    fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
    # Add percentage in center
    fig_donut.add_annotation(text=f"{int(monthly_pct)}%", x=0.5, y=0.5, font_size=40, showarrow=False, font_color="#1a73e8")
    
    st.plotly_chart(fig_donut, use_container_width=True)

db.close()
