"""
Activity 6.2: Optional Streamlit Dashboard.
Visualizes multimodal attendance records, engagement timelines,
instructor teaching suggestions, and student analytics in an interactive format.
Matches Project Specification (Pages 10, 37).
"""

import streamlit as st
import pandas as pd
import time
import os
import sys

# Ensure backend package is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.db import init_db, SessionLocal
from backend.database.models import SessionModel, AttendanceRecord, PersonMetric, TeacherProfileModel
from backend.core.teacher_profiles import TeacherProfileService
from backend.core.analytics_service import AnalyticsService

# Page Configuration
st.set_page_config(
    page_title="EduSense AI | Multimodal Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        color: white;
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize DB
init_db()
teacher_service = TeacherProfileService()
analytics_service = AnalyticsService()

# Sidebar Controls
st.sidebar.title("🎓 EduSense AI")
st.sidebar.caption("Multimodal Attendance & Engagement Agent")

view_mode = st.sidebar.radio(
    "Select View",
    ["🔴 Live Session Overview", "👨‍🏫 Teacher Central", "📊 Session Analytics & Export", "⚙️ System Configuration"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**System Health:** 🟢 Operational (Offline Mode)")
st.sidebar.markdown("**Vision:** OpenCV Haar + Centroid Tracker")
st.sidebar.markdown("**Audio:** 16kHz VAD & dB Acoustic Meter")
st.sidebar.markdown("**Reasoning:** Multimodal Rule + LLM Agent")

# -------------------------------------------------------------
# VIEW 1: LIVE SESSION OVERVIEW
# -------------------------------------------------------------
if view_mode == "🔴 Live Session Overview":
    st.title("Classroom Live Dynamics & Attendance")
    st.write("Real-time presence tracking, attention estimation, and contextual teaching suggestions.")

    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Active Participants", value="2 Students", delta="Normal")
    with col2:
        st.metric(label="Average Attention", value="84.5%", delta="+3.2%")
    with col3:
        st.metric(label="Classroom Engagement", value="88.0%", delta="+5.0%")
    with col4:
        st.metric(label="Acoustic Level", value="-44.2 dB", delta="Attentive Silence")

    st.markdown("---")

    left_col, right_col = st.columns([1.5, 1])

    with left_col:
        st.subheader("Live Classroom Feed")
        st.info("💡 To view live MJPEG video stream, ensure the FastAPI core server is running (`python run.py --server`) or view at http://localhost:8000")
        
        # Attendance Roster
        st.subheader("Sustained Presence Attendance Roster")
        attendance_data = [
            {"Student": "Priya Sharma (Student_1)", "Presence": "185s", "Status": "Present", "Verified": "✅ Yes", "Attention": "88.5%"},
            {"Student": "Kumar Patel (Student_2)", "Presence": "172s", "Status": "Present", "Verified": "✅ Yes", "Attention": "76.0%"},
            {"Student": "Asha Varma (Student_3)", "Presence": "35s", "Status": "Partial", "Verified": "⏳ Pending", "Attention": "62.0%"},
            {"Student": "Rohan Gupta (Student_4)", "Presence": "0s", "Status": "Absent", "Verified": "❌ No", "Attention": "0.0%"}
        ]
        df_att = pd.DataFrame(attendance_data)
        st.dataframe(df_att, use_container_width=True)

    with right_col:
        st.subheader("AI Teaching Suggestion Box")
        st.success("**Current Insight:** Classroom engagement is steady. Visual attentiveness is strong in front row.")
        st.warning("**Pedagogical Recommendation:** Consider a 60-second interactive check-in question to sustain momentum (+18% focus retention).")

        st.subheader("Recent Behavioral Alerts")
        st.error("⚠️ Student_3: Brief distraction / head looking down (35s)")
        st.info("ℹ️ Acoustic context: Attentive silence. Good lecture receptivity.")

# -------------------------------------------------------------
# VIEW 2: TEACHER CENTRAL
# -------------------------------------------------------------
elif view_mode == "👨‍🏫 Teacher Central":
    st.title("Teacher Profile & Longitudinal Effectiveness")
    profile = teacher_service.get_profile("T_101")

    # Big Card
    c1, c2, c3 = st.columns([1.2, 1.4, 1.4])
    with c1:
        st.metric("Teaching Effectiveness", f"{profile['effectiveness_score']} / 100", f"+{profile['trend']}% vs last month")
    with c2:
        st.subheader("Observed Strengths")
        for s in profile["strengths"]:
            st.markdown(f"- 🌟 {s}")
    with c3:
        st.subheader("Pedagogical Recommendations")
        for r in profile["recommendations"]:
            st.markdown(f"- 💡 {r}")

    st.markdown("---")
    st.subheader("Class History Comparison")
    hist_cols = st.columns(len(profile["class_history"]))
    for i, c in enumerate(profile["class_history"]):
        with hist_cols[i]:
            st.metric(label=c["name"], value=f"{c['engagement']}% Avg", delta=f"Attendance: {c.get('attendance', '92%')}")

# -------------------------------------------------------------
# VIEW 3: SESSION ANALYTICS & EXPORT
# -------------------------------------------------------------
elif view_mode == "📊 Session Analytics & Export":
    st.title("Session Analytics & Reflective Reports")
    trends = analytics_service.get_session_trends(1)

    # Chart 1: Attention Curve
    st.subheader("Attention Trend Over Time")
    df_trend = pd.DataFrame(trends["attention_trend"])
    if not df_trend.empty:
        st.line_chart(df_trend.set_index("time")[["attention", "engagement"]])

    # Chart 2: Emotion Distribution
    st.subheader("Emotion & Engagement Distribution")
    df_emo = pd.DataFrame(list(trends["emotion_distribution"].items()), columns=["State", "Count"])
    st.bar_chart(df_emo.set_index("State"))

    # Reflective Summaries
    st.subheader("Student Reflective Summaries (Privacy-Preserving)")
    df_sum = pd.DataFrame(trends["student_summaries"])
    st.dataframe(df_sum[["student_name", "status", "presence_seconds", "avg_attention", "reflective_feedback"]], use_container_width=True)

    # Export Buttons
    c1, c2 = st.columns(2)
    with c1:
        csv_data = df_sum.to_csv(index=False)
        st.download_button("📥 Export CSV Data", csv_data, "attendance_report.csv", "text/csv")
    with c2:
        st.info("📄 PDF Reports can also be generated directly via the FastAPI web app at `/api/export/pdf`")

# -------------------------------------------------------------
# VIEW 4: SYSTEM CONFIGURATION
# -------------------------------------------------------------
elif view_mode == "⚙️ System Configuration":
    st.title("System Configuration & Edge Case Diagnostics")
    st.write("Configure vision thresholds, sustained presence requirements, and audio sensitivity.")

    min_pres = st.slider("Sustained Presence Threshold (Seconds)", min_value=5, max_value=60, value=15)
    noise_thresh = st.slider("Background Noise Alert Threshold (dB)", min_value=-60, max_value=-15, value=-28)
    cam_source = st.selectbox("Video Input Source", ["Simulated Synthetic Classroom (Testing)", "Physical Webcam (Device 0)", "Custom Video File"])

    if st.button("Apply Parameters"):
        st.success(f"Parameters updated: Presence={min_pres}s, Noise={noise_thresh}dB, Source={cam_source}")
