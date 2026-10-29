# Multimodal Attendance & Engagement Agent (EduSense AI)

> **An AI-powered, privacy-preserving classroom intelligence system integrating Computer Vision, Audio Signal Processing, and Agent-Based Reasoning.**

---

## 📌 Executive Summary & Problem Statement

In educational institutions and professional training environments, attendance tracking remains largely manual or limited to basic biometric systems that fail to capture meaningful engagement and participation context. These traditional approaches are time-consuming, prone to inaccuracies, and provide no insight into learner attention, interaction patterns, or session effectiveness. As classrooms increasingly adopt digital tools, there is a growing need for intelligent systems that can move beyond simple presence detection.

To address this challenge, the **Multimodal Attendance & Engagement Agent** was developed as an AI-powered, privacy-preserving classroom intelligence system. The project integrates **computer vision**, **audio signal processing**, and **agent-based reasoning** to:
1. **Automatically track attendance** based on **sustained presence** (rejecting single-frame false positives).
2. **Analyze real-time engagement trends** by fusing visual attention cues (head pose, movement, inactivity) with acoustic indicators (ambient noise level in dB, voice activity detection, speech vs. silence ratio).
3. **Generate AI-driven teaching suggestions** acting as an assistive, non-prescriptive decision-support tool.
4. **Provide reflective student session analytics** without peer rankings or punitive metrics.

Designed to operate **entirely offline**, the system ensures ethical, privacy-preserving deployment while offering actionable insights that support both educators and learners.

---

## 🚀 Key Scenarios Addressed

### Scenario 1: Automated Attendance Tracking
During a classroom session, the system processes a live webcam feed or pre-recorded classroom video. Instead of marking attendance based on a single frame, the system accumulates participant presence over time using continuous spatial tracking. Attendance is confirmed only when cumulative presence exceeds a predefined sustained threshold (e.g., $\ge 15$ seconds), eliminating false positives from accidental glances or hallway passersby. Structured, timestamped attendance logs are generated automatically.

### Scenario 2: Engagement and Session Dynamics Analysis
The system continuously observes behavioral indicators such as head pose orientation, movement frequency, inactivity duration, and room acoustics. These multimodal signals are synchronized into discrete temporal windows (e.g., 2–5 second snapshots) to compute transparent, explainable engagement scores ($0–100$) and track session dynamics over time (identifying attention dips, collaborative discussion peaks, and pacing issues).

### Scenario 3: AI-Driven Teaching Suggestions
Using real-time engagement trends, the agent delivers contextual pedagogical recommendations:
- **Immediate Behavioral Alerts**: Flagging individual distraction (e.g., *Student [ID] is distracted (34% attention)*).
- **Classroom Warnings**: Detecting collective attention drops below 60% and advising quick check-ins or interactive poll breaks (+18% engagement boost).
- **Teacher Effectiveness Tracking**: Longitudinal instructor profile tracking (87.5/100 effectiveness, +12% monthly trend) with cohort comparisons (CS101 Today, CS101 Yesterday, Math Workshop).

---

## 🏛 Technical Architecture

```
+-----------------------------------------------------------------------------------+
|                                  FRONTEND LAYER                                   |
|  - EduSense AI Dark Dashboard (HTML5 / CSS3 / Vanilla JS Controller)             |
|  - Optional Streamlit Analytics Dashboard (Activity 6.2)                         |
|  - Web Audio API Live Microphone Streamer (AudioCapture.jsx / audio-capture.js)    |
+-----------------------------------------------------------------------------------+
                                        |  HTTP / WebSockets (/ws/audio, /video_feed)
                                        v
+-----------------------------------------------------------------------------------+
|                              BACKEND & AI GATEWAY                                 |
|  - FastAPI (REST Endpoints & WebSocket Handlers)                                 |
|  - Uvicorn ASGI Server                                                           |
+-----------------------------------------------------------------------------------+
        |                                       |                          |
        v                                       v                          v
+-----------------------+     +-----------------------+     +-----------------------+
|     VISION MODULE     |     |     AUDIO MODULE      |     |  MULTIMODAL FUSION &  |
| - FaceDetector        |     | - AudioAnalyzer       |     |     SCORING ENGINE    |
|   (Haar / Contour)    |     | - 16kHz PCM Processor |     | - MultimodalFusion    |
| - CentroidTracker     |     | - Ambient dB Meter    |     | - EngagementScorer    |
| - Sustained Presence  |     | - VAD & Speech Ratio  |     | - MultimodalAgent     |
|   Attendance Logic    |     | - Acoustic Patterns   |     |   (Orchestrator Loop) |
+-----------------------+     +-----------------------+     +-----------------------+
                                                                       |
                                                                       v
+-----------------------------------------------------------------------------------+
|                        ANALYTICS & RECOMMENDATION LAYER                           |
|  - RecommendationsEngine (Immediate Alerts & Threshold Warnings)                 |
|  - AISuggestionEngine (Offline Rule Reasoning & Groq / Gemini LLM Integration)   |
|  - TeacherProfileService (Effectiveness Score 87.5/100, Longitudinal History)     |
|  - AnalyticsService (Timeline Curves, Emotion Distributions, Reflective Summaries)|
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         STORAGE & EXPORT UTILITY LAYER                            |
|  - SQLite Database with SQLAlchemy ORM (SessionModel, AttendanceRecord, Metric)   |
|  - ReportExporter (Instant CSV Download & Styled Printable PDF/HTML Reports)      |
|  - SyntheticClassroomGenerator (Offline Testing & Simulator Fallback)             |
+-----------------------------------------------------------------------------------+
```

---

## 📋 Milestone & Activity Mapping (From Project Specification)

| Milestone | Activity | Component | Implementation File | Status |
|---|---|---|---|---|
| **Milestone 1** | Activity 1.1 | Requirements Specification | `requirements.txt` | ✅ Complete |
| | Activity 1.2 | Environment Setup & Verification | Virtual environment & dependencies | ✅ Complete |
| **Milestone 2** | Activity 2.1 | Face Detection & Centroid Tracking | `backend/core/face_detection.py`, `backend/core/camera_service.py` | ✅ Complete |
| | Activity 2.2 | Sustained Presence Attendance Logic | `backend/core/face_recognition.py` | ✅ Complete |
| **Milestone 3** | Activity 3.1 | Audio Signal Extraction (16 kHz PCM) | `backend/core/audio_analysis.py` | ✅ Complete |
| | Activity 3.2 | Noise & Speech Activity Analysis | `backend/core/audio_analysis.py`, `components/AudioCapture.jsx` | ✅ Complete |
| **Milestone 4** | Activity 4.1 | Multimodal Agent Implementation | `backend/core/multimodal_agent.py` | ✅ Complete |
| | Activity 4.2 | Multimodal Signal Fusion | `backend/core/fusion_engine.py` | ✅ Complete |
| | Activity 4.3 | Explainable Engagement Scoring Logic | `backend/core/engagement_scoring.py` | ✅ Complete |
| **Milestone 5** | Activity 5.1 | Teaching Suggestion Logic | `backend/core/recommendations_engine.py`, `backend/core/teacher_profiles.py` | ✅ Complete |
| | Activity 5.2 | Student Session Analytics Generation | `backend/core/analytics_service.py` | ✅ Complete |
| **Milestone 6** | Activity 6.1 | Run Core FastAPI Application | `backend/main.py`, `run.py` | ✅ Complete |
| | Activity 6.2 | Launch Optional Streamlit Dashboard | `streamlit_app.py` | ✅ Complete |
| | Activity 6.3 | Validate Outputs and Edge Cases | `tests/test_*.py` (20 automated tests) | ✅ Complete |

---

## 💡 Multimodal Engagement Scoring Formula

The system computes an explainable, transparent engagement index ($E \in [0, 100]$) computed as a weighted combination of behavioral cues:

$$E = w_v \cdot V + w_m \cdot M + w_a \cdot A$$

Where:
- **$V$ (Visual Attention Factor, $w_v = 0.45$):** Evaluated from head pose (forward $= 92\%$, turned away $= 60\%$, looking down $= 40\%$) and eye presence.
- **$M$ (Motion & Posture Dynamics, $w_m = 0.25$):** Natural movement ($1–25$ px/s) receives high scores ($90\%$), while prolonged stillness ($>12$s) incurs inactivity penalties.
- **$A$ (Acoustic Context Factor, $w_a = 0.30$):** Modulates score based on classroom acoustic state (Attentive Silence $= 85\%$, Active Discussion $= 95\%$, High Noise Disruption $= 50\%$).

### Behavioral Classifications:
- **$82 - 100\%$:** `Focused`
- **$68 - 81\%$:** `Engaged`
- **$50 - 67\%$:** `Neutral`
- **$< 50\%$ (or Inactive $>12$s):** `Distracted` / `Drowsy`

---

## 🛠 Installation & Quick Start

### 1. Prerequisites
- Python 3.9, 3.10, or 3.11
- Modern Web Browser (Chrome, Edge, Firefox)
- Optional: Physical webcam and microphone (system automatically falls back to built-in synthetic classroom simulation if no hardware is detected).

### 2. Install Dependencies
```bash
cd "C:\Users\Moon\.gemini\antigravity\scratch\multimodal-attendance-engagement-agent"
pip install -r requirements.txt
```

### 3. Launch the Application

#### Option A: Core Application & Modern Dark Dashboard (Recommended)
```bash
python run.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to access:
- **Live Session Dashboard:** Live video HUD, acoustic dB gauge, live attendance roster, AI suggestions.
- **Teacher Central:** Teaching effectiveness score ($87.5/100$, $+12\%$), strengths, recommendations, class history.
- **Session Analytics:** Attention trend line chart, emotion bar chart, reflective feedback table, instant **PDF Report** and **CSV Data** downloads.
- **API Documentation:** Interactive Swagger UI at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

#### Option B: Optional Streamlit Dashboard (Activity 6.2)
```bash
python run.py --streamlit
```
Open **[http://localhost:8501](http://localhost:8501)** to explore the Streamlit interface.

#### Option C: Run Validation Test Suite (Activity 6.3)
```bash
python run.py --test
```
Runs 20 automated unit and integration tests verifying vision, audio, fusion, recommendations, and API endpoints.

---

## 🔒 Privacy & Ethical AI Guarantees

1. **100% Offline Processing:** All computer vision tracking, audio signal processing, and scoring logic run on-device without streaming video or audio data to any cloud service.
2. **Presence-Based Thresholding:** Eliminates false attendance marks from single-frame detections or transient bystanders.
3. **Reflective, Non-Punitive Feedback:** Student analytics provide reflective self-improvement summaries without public shaming, punitive grading, or peer rankings.
4. **Assistive Decision Support:** The AI suggestion box serves strictly as an assistive tool for instructors, preserving full pedagogical human agency.

---

## 📁 Repository Directory Structure

```
multimodal-attendance-engagement-agent/
│
├── requirements.txt                   # Dependency manifest
├── README.md                          # Comprehensive documentation
├── run.py                             # Unified CLI & server launcher
├── streamlit_app.py                   # Activity 6.2 Streamlit dashboard
│
├── backend/
│   ├── main.py                        # FastAPI application, WebSockets & REST APIs
│   │
│   ├── core/
│   │   ├── face_detection.py          # Activity 2.1: Face detection, landmarks, head pose
│   │   ├── face_recognition.py        # Activity 2.2: Presence-based attendance logic
│   │   ├── camera_service.py          # Activity 2.1: Webcam, recorded video, synthetic feed
│   │   ├── audio_analysis.py          # Activity 3.1 & 3.2: Noise level (dB), VAD, sound patterns
│   │   ├── fusion_engine.py           # Activity 4.2: Multimodal signal fusion
│   │   ├── engagement_scoring.py      # Activity 4.3: Transparent engagement scoring formula
│   │   ├── multimodal_agent.py        # Activity 4.1: Multimodal agent orchestrator
│   │   ├── ai_suggestions.py          # Activity 4.1 & 5.1: AI suggestion engine (offline + LLM)
│   │   ├── recommendations_engine.py  # Activity 5.1: Real-time alerts & classroom warnings
│   │   ├── teacher_profiles.py        # Activity 5.1: Teacher profile service & history
│   │   └── analytics_service.py       # Activity 5.2: Student session analytics generation
│   │
│   ├── database/
│   │   ├── db.py                      # SQLAlchemy SQLite engine & seed data
│   │   └── models.py                  # SessionModel, AttendanceRecord, PersonMetric, etc.
│   │
│   └── utils/
│       ├── report_exporter.py         # PDF and CSV report generator
│       └── synthetic_feed.py          # Synthetic classroom simulator
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css              # Dark theme styling matching project screens
│   │   └── js/
│   │       ├── app.js                 # Dashboard controller, live polling & canvas charts
│   │       └── audio-capture.js       # Activity 3.2 Web Audio API client streamer
│   └── templates/
│       └── index.html                 # Multi-tab modern UI (Live, Teacher, Analytics)
│
├── components/
│   └── AudioCapture.jsx               # React component from Project Specification (Pages 24-25)
│
├── data/
│   ├── registered_students/           # Classroom student roster & metadata
│   └── attendance_logs/               # Exported CSV attendance reports
│
└── tests/
    ├── test_vision.py                 # Vision & sustained presence tests
    ├── test_audio.py                  # Audio dB & VAD tests
    ├── test_multimodal.py             # Fusion & scoring tests
    ├── test_recommendations.py        # Suggestions & teacher profile tests
    └── test_api.py                    # REST API & export tests
```
