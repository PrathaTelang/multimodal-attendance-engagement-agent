"""
Activity 6.1: Run Core Application (FastAPI Backend Server).
Coordinates WebSockets, REST APIs, Video Streaming, and the Multimodal Agent.
Matches the technical architecture described in Project Specifications (Pages 3, 13, 36).
"""

import os
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .core.multimodal_agent import MultimodalAgent
from .core.teacher_profiles import TeacherProfileService
from .core.analytics_service import AnalyticsService
from .database.db import init_db, get_db
from .utils.report_exporter import ReportExporter

# Initialize database schema
init_db()

app = FastAPI(
    title="Multimodal Attendance & Engagement Agent API",
    description="Privacy-preserving classroom intelligence platform combining CV, Audio, and Agent Reasoning.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate central multimodal agent
# Defaults to synthetic classroom generator if physical camera not active
agent = MultimodalAgent(camera_id=0, min_presence_sec=10.0, use_synthetic=False)
teacher_service = TeacherProfileService()
analytics_service = AnalyticsService()

# Serve frontend static assets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Pydantic Schemas
class StartSessionRequest(BaseModel):
    session_name: str = "CS101: Multimodal AI & Learning Systems"
    teacher_id: str = "T_101"
    camera_source: str = "auto"  # "auto", "webcam", "synthetic"


class RegisterStudentRequest(BaseModel):
    student_id: str
    name: str
    roll_no: str = ""
    department: str = "Computer Science"


@app.on_event("startup")
async def startup_event():
    print("[Server] Starting Multimodal Attendance & Engagement Agent...")
    # Auto-start default demo session for instant out-of-the-box readiness
    agent.start_session(session_name="CS101: Multimodal AI & Learning Systems", teacher_id="T_101")


@app.on_event("shutdown")
async def shutdown_event():
    print("[Server] Shutting down agent...")
    agent.stop_session()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the main interactive dashboard."""
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Multimodal Attendance & Engagement Agent is running.</h1><p>Visit /docs for API documentation.</p>")


@app.get("/video_feed")
async def video_feed():
    """
    MJPEG video streaming endpoint.
    Streams annotated classroom video with real-time bounding boxes and attention tags.
    """
    def frame_generator():
        while True:
            frame_bytes = agent.camera_service.get_jpeg_bytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.04)  # ~25 FPS

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for ingesting live microphone audio chunks
    from the frontend (Web Audio API). Matches Activity 3.2.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # Analyze chunk through audio module
            audio_metrics = agent.process_incoming_audio(data)
            # Reply with real-time metrics back to client
            await websocket.send_json(audio_metrics)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocket Audio] Connection closed: {e}")


@app.post("/api/session/start")
async def start_session(req: StartSessionRequest):
    """Starts attendance and multimodal engagement tracking."""
    if req.camera_source == "synthetic":
        agent.camera_service.use_synthetic = True
    elif req.camera_source == "webcam":
        agent.camera_service.use_synthetic = False

    session_id = agent.start_session(session_name=req.session_name, teacher_id=req.teacher_id)
    return {"status": "started", "session_id": session_id, "session_name": req.session_name}


@app.post("/api/session/stop")
async def stop_session():
    """Stops the active session and finalizes reports."""
    agent.stop_session()
    return {"status": "stopped", "message": "Session finalized. Attendance logs recorded."}


@app.get("/api/session/status")
async def get_session_status():
    """Returns current live agent status for real-time dashboard updates."""
    status = agent.get_status()
    return JSONResponse(content=status)


@app.get("/api/attendance")
async def get_attendance():
    """Returns sustained-presence attendance records."""
    records = agent.face_recognizer.get_attendance_records(agent.current_session_id)
    return JSONResponse(content=records)


@app.post("/api/students/register")
async def register_student(req: RegisterStudentRequest):
    """Registers a new student into the classroom roster."""
    success = agent.face_recognizer.register_student(
        student_id=req.student_id,
        name=req.name,
        roll_no=req.roll_no,
        department=req.department
    )
    return {"status": "registered" if success else "failed", "student_id": req.student_id}


@app.get("/api/teacher/profile")
async def get_teacher_profile(teacher_id: str = "T_101"):
    """Returns instructor effectiveness profile and class history comparison."""
    profile = teacher_service.get_profile(teacher_id)
    return JSONResponse(content=profile)


@app.get("/api/analytics/trends")
async def get_analytics_trends():
    """Returns time-series attention trends and emotion distribution."""
    trends = analytics_service.get_session_trends(agent.current_session_id)
    return JSONResponse(content=trends)


@app.get("/api/export/csv")
async def export_attendance_csv():
    """Downloads attendance records as a CSV file."""
    records = agent.face_recognizer.get_attendance_records(agent.current_session_id)
    csv_data = ReportExporter.export_attendance_csv(records)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_session_{agent.current_session_id}.csv"}
    )


@app.get("/api/export/pdf")
async def export_session_pdf():
    """Downloads styled printable session report."""
    status = agent.get_status()
    records = agent.face_recognizer.get_attendance_records(agent.current_session_id)
    pdf_bytes = ReportExporter.export_session_pdf(agent.current_session_id, status, records)
    return Response(
        content=pdf_bytes,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=session_report_{agent.current_session_id}.html"}
    )
