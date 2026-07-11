import streamlit as st
from datetime import date, timedelta
from database import get_db_session
from models import RevisionQueue
import pandas as pd

st.title("Revision Queue")
st.caption("Stay on top of your spaced repetition schedule.")

db = get_db_session()
today = date.today()

# Get pending revisions (due today or earlier)
pending_revisions = db.query(RevisionQueue).filter(
    RevisionQueue.completed == False,
    RevisionQueue.revision_date <= today
).order_by(RevisionQueue.revision_date.asc()).all()

# Get future revisions (next 7 days)
future_revisions = db.query(RevisionQueue).filter(
    RevisionQueue.completed == False,
    RevisionQueue.revision_date > today,
    RevisionQueue.revision_date <= today + timedelta(days=7)
).order_by(RevisionQueue.revision_date.asc()).all()

st.subheader("Due For Revision")
if not pending_revisions:
    st.success("All caught up! No pending revisions for today.")
else:
    for rev in pending_revisions:
        with st.container(border=True):
            rc1, rc2, rc3 = st.columns([4, 2, 2])
            sess = rev.learning_session
            with rc1:
                subject_name = sess.subject.name if sess.subject else "Unknown Subject"
                st.markdown(f"**{subject_name}** - {sess.topic}")
                st.caption(f"Original Session: {sess.completion_date}")
            with rc2:
                days_overdue = (today - rev.revision_date).days
                color = "red" if days_overdue > 0 else "orange"
                st.markdown(f"**Stage: R{rev.revision_stage}**")
                if days_overdue > 0:
                    st.caption(f"<span style='color:{color}'>{days_overdue} days overdue</span>", unsafe_allow_html=True)
                else:
                    st.caption(f"<span style='color:{color}'>Due Today</span>", unsafe_allow_html=True)
            with rc3:
                if st.button("Complete Revision", key=f"rev_{rev.id}", type="primary"):
                    rev.completed = True
                    db.commit()
                    st.rerun()

st.write("---")
st.subheader("Coming Up (Next 7 Days)")
if not future_revisions:
    st.info("No upcoming revisions in the next week.")
else:
    data = []
    for rev in future_revisions:
        sess = rev.learning_session
        subject_name = sess.subject.name if sess and sess.subject else "Unknown Subject"
        data.append({
            "Date": rev.revision_date.strftime("%b %d"),
            "Subject": subject_name,
            "Topic": sess.topic if sess else "Unknown",
            "Stage": f"R{rev.revision_stage}"
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

db.close()
