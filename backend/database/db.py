"""
Database connection and session initialization for SQLite.
Supports offline, privacy-preserving, zero-cloud storage.
"""

import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, TeacherProfileModel

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "classroom_intelligence.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables and seed default instructor profile if not present."""
    Base.metadata.create_all(bind=engine)
    
    # Seed default teacher profile matching UI screenshot (Pages 32, 39, 40)
    db = SessionLocal()
    try:
        existing = db.query(TeacherProfileModel).filter_by(teacher_id="T_101").first()
        if not existing:
            default_profile = TeacherProfileModel(
                teacher_id="T_101",
                teacher_name="Prof. Alex Mercer",
                effectiveness_score=87.5,
                trend=12.0,
                strengths_json=json.dumps([
                    "High engagement sessions (85%+)",
                    "Emotion diversity management",
                    "Pacing synchronization with student audio responses"
                ]),
                recommendations_json=json.dumps([
                    "Try interactive polls (boost +18%)",
                    "Short video breaks (+25% re-engagement)",
                    "Address quiet corner disengagement after 20 mins"
                ]),
                class_history_json=json.dumps([
                    {"name": "CS101 (Today)", "engagement": 85, "attendance": "94%"},
                    {"name": "CS101 (Yesterday)", "engagement": 78, "attendance": "88%"},
                    {"name": "Math Workshop", "engagement": 92, "attendance": "96%"}
                ])
            )
            db.add(default_profile)
            db.commit()
    finally:
        db.close()


def get_db():
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
