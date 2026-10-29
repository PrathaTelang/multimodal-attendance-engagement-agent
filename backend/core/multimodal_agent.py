"""
Activity 4.1: Multimodal Agent Implementation.
Core intelligence orchestrator integrating Vision, Audio, Fusion, Attendance,
and Recommendations into an autonomous classroom decision-support agent.
"""

import time
import threading
from datetime import datetime
from .camera_service import CameraService
from .face_recognition import FaceRecognizer
from .audio_analysis import AudioAnalyzer
from .fusion_engine import MultimodalFusionEngine
from .recommendations_engine import RecommendationsEngine
from .ai_suggestions import AISuggestionEngine
from ..database.db import SessionLocal
from ..database.models import SessionModel, AttendanceRecord, PersonMetric, TeachingSuggestionModel


class MultimodalAgent:
    def __init__(self, camera_id=0, min_presence_sec=15.0, use_synthetic=False):
        self.camera_service = CameraService(camera_id=camera_id, use_synthetic=use_synthetic)
        self.face_recognizer = FaceRecognizer(min_presence_seconds=min_presence_sec)
        self.audio_analyzer = AudioAnalyzer()
        self.fusion_engine = MultimodalFusionEngine()
        self.recommendations_engine = RecommendationsEngine()
        self.ai_engine = AISuggestionEngine()

        self.current_session_id = 1
        self.session_active = False
        self.session_start_time = None
        self._agent_thread = None
        self._lock = threading.Lock()

        # Cache of latest agent status
        self.latest_status = {
            "session_active": False,
            "session_duration_seconds": 0,
            "active_participants": 0,
            "avg_attention": 0.0,
            "avg_engagement": 0.0,
            "audio": {"db_level": -45.0, "speech_ratio": 0.0, "acoustic_state": "attentive_silence"},
            "alerts": [],
            "ai_insight": {
                "insight": "System initialized and waiting to start session.",
                "recommendation": "Click 'Start Session' to begin multimodal tracking."
            },
            "students": []
        }

    def start_session(self, session_name="CS101 Classroom Intelligence", teacher_id="T_101"):
        """Starts a new multimodal tracking session."""
        with self._lock:
            if self.session_active:
                return self.current_session_id

            self.session_active = True
            self.session_start_time = time.time()
            self.face_recognizer.reset_session()
            self.camera_service.start()

            # Record session start in DB
            db = SessionLocal()
            try:
                new_sess = SessionModel(
                    session_name=session_name,
                    teacher_id=teacher_id,
                    start_time=datetime.utcnow(),
                    is_active=True
                )
                db.add(new_sess)
                db.commit()
                db.refresh(new_sess)
                self.current_session_id = new_sess.id
            finally:
                db.close()

            self._agent_thread = threading.Thread(target=self._run_agent_cycle, daemon=True)
            self._agent_thread.start()
            print(f"[MultimodalAgent] Session #{self.current_session_id} started: '{session_name}'")
            return self.current_session_id

    def stop_session(self):
        """Stops active session, finalizes attendance records and aggregates in DB."""
        with self._lock:
            if not self.session_active:
                return

            self.session_active = False
            self.camera_service.stop()

            # Finalize DB session
            db = SessionLocal()
            try:
                sess = db.query(SessionModel).filter_by(id=self.current_session_id).first()
                if sess:
                    sess.is_active = False
                    sess.end_time = datetime.utcnow()
                    
                    # Store final attendance records
                    records = self.face_recognizer.get_attendance_records(self.current_session_id)
                    sess.total_participants = len([r for r in records if r["attendance_status"] == "Present"])
                    
                    if self.latest_status.get("avg_engagement", 0) > 0:
                        sess.avg_engagement = self.latest_status["avg_engagement"]

                    for r in records:
                        att_entry = AttendanceRecord(
                            session_id=self.current_session_id,
                            person_id=r["person_id"],
                            student_name=r["student_name"],
                            total_presence_seconds=r["presence_duration_seconds"],
                            attendance_status=r["attendance_status"],
                            sustained_presence_verified=r["sustained_presence_verified"],
                            avg_attention_score=r["avg_attention_score"]
                        )
                        db.add(att_entry)

                    db.commit()
            except Exception as e:
                print(f"[MultimodalAgent] Error finalizing session in DB: {e}")
            finally:
                db.close()

            print(f"[MultimodalAgent] Session #{self.current_session_id} stopped.")

    def process_incoming_audio(self, audio_bytes):
        """Callback for live microphone audio chunks sent from browser WebSocket."""
        return self.audio_analyzer.analyze_audio_chunk(audio_bytes)

    def _run_agent_cycle(self):
        """Main agent loop running multimodal reasoning every 1.0 second."""
        last_db_persist_time = time.time()
        last_ai_insight_time = 0

        while self.session_active:
            try:
                loop_start = time.time()
                
                # 1. Fetch latest tracks from vision module
                tracks = self.camera_service.get_latest_tracks()

                # 2. Update sustained presence attendance tracker
                self.face_recognizer.update_presence(tracks, dt=1.0)

                # 3. Fetch latest audio status (or simulate if no mic input arrived)
                audio_metrics = self.audio_analyzer.analyze_audio_chunk(
                    self.audio_analyzer.simulate_audio_chunk(mode="lecture")
                )

                # 4. Multimodal Fusion
                fused = self.fusion_engine.fuse(tracks, audio_metrics, session_id=self.current_session_id)

                # 5. Form session status for recommendation engine
                people_status = []
                for s in fused["vision"]["students"]:
                    people_status.append({
                        "id": s["person_id"],
                        "person_id": s["person_id"],
                        "attention": s["attention_score"],
                        "engagement": s["engagement_score"],
                        "inactivity_seconds": s.get("inactivity_seconds", 0.0),
                        "head_pose": s["head_pose"]
                    })

                session_payload = {
                    "people": people_status,
                    "audio": fused["audio"],
                    "aggregate": fused["aggregate"],
                    "vision": fused["vision"]
                }

                # 6. Rule-based immediate recommendations
                realtime_alerts = self.recommendations_engine.generate_realtime_recommendations(session_payload)

                # 7. AI pedagogical suggestions (every 8-10 seconds)
                if loop_start - last_ai_insight_time > 8.0:
                    ai_res = self.ai_engine.generate_classroom_insight(fused)
                    last_ai_insight_time = loop_start
                else:
                    ai_res = self.latest_status.get("ai_insight", {})

                # 8. Update cache
                duration = int(loop_start - self.session_start_time) if self.session_start_time else 0
                
                with self._lock:
                    self.latest_status = {
                        "session_id": self.current_session_id,
                        "session_active": self.session_active,
                        "session_duration_seconds": duration,
                        "active_participants": len(people_status),
                        "avg_attention": fused["aggregate"]["avg_attention"],
                        "avg_engagement": fused["aggregate"]["avg_engagement"],
                        "classroom_status": fused["aggregate"]["status"],
                        "audio": fused["audio"],
                        "alerts": realtime_alerts,
                        "ai_insight": ai_res,
                        "students": people_status
                    }

                # 9. Periodic DB Persistence (every 5 seconds)
                if loop_start - last_db_persist_time >= 5.0:
                    last_db_persist_time = loop_start
                    self._persist_cycle_data(people_status, realtime_alerts)

                time.sleep(1.0)

            except Exception as e:
                print(f"[MultimodalAgent] Loop exception: {e}")
                time.sleep(1.0)

    def _persist_cycle_data(self, students, alerts):
        """Asynchronously persists time-series metrics to SQLite."""
        db = SessionLocal()
        try:
            for s in students:
                metric = PersonMetric(
                    session_id=self.current_session_id,
                    person_id=s["person_id"],
                    timestamp=datetime.utcnow(),
                    attention_score=s["attention"],
                    engagement_score=s["engagement"],
                    head_pose=s.get("head_pose", "forward"),
                    is_active=True
                )
                db.add(metric)

            # Record top alert if present
            if alerts:
                top_alert = alerts[0]
                sug = TeachingSuggestionModel(
                    session_id=self.current_session_id,
                    timestamp=datetime.utcnow(),
                    suggestion_type=top_alert.get("type", "alert"),
                    message=top_alert.get("message", ""),
                    severity=top_alert.get("severity", "info")
                )
                db.add(sug)

            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    def get_status(self):
        """Returns snapshot of current agent status."""
        with self._lock:
            return dict(self.latest_status)
