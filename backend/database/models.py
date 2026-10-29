"""
Database Models for Multimodal Attendance & Engagement Agent.
Follows the schema specified in Project Specifications (Pages 31-35).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_name = Column(String(100), default="Classroom Session")
    teacher_id = Column(String(50), default="T_101")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    total_participants = Column(Integer, default=0)
    avg_engagement = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")
    metrics = relationship("PersonMetric", back_populates="session", cascade="all, delete-orphan")
    suggestions = relationship("TeachingSuggestionModel", back_populates="session", cascade="all, delete-orphan")


class AttendanceRecord(Base):
    """
    Session Person record tracking sustained presence logic for attendance marking.
    Prevents single-frame false positives by requiring cumulative presence duration.
    """
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    person_id = Column(String(50), index=True, nullable=False)
    student_name = Column(String(100), default="Student")
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_presence_seconds = Column(Float, default=0.0)
    attendance_status = Column(String(20), default="Pending")  # "Present", "Partial", "Absent"
    sustained_presence_verified = Column(Boolean, default=False)
    avg_attention_score = Column(Float, default=0.0)
    avg_engagement_score = Column(Float, default=0.0)

    session = relationship("SessionModel", back_populates="attendance_records")


# Alias for backward-compatibility with prompt snippet
SessionPerson = AttendanceRecord


class PersonMetric(Base):
    """
    Time-series metric snapshots for individual participants.
    Used for attention trend curves, emotion distributions, and reflective summaries.
    """
    __tablename__ = "person_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    person_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    attention_score = Column(Float, default=0.0)  # 0 to 100
    engagement_score = Column(Float, default=0.0)  # 0 to 100
    emotion = Column(String(30), default="focused")  # focused, engaged, neutral, distracted, drowsy
    head_pose = Column(String(30), default="forward")  # forward, turned_away, looking_down
    is_active = Column(Boolean, default=True)
    movement_intensity = Column(Float, default=0.0)

    session = relationship("SessionModel", back_populates="metrics")


class TeachingSuggestionModel(Base):
    """
    Stored AI-driven and rule-based suggestions generated during sessions.
    """
    __tablename__ = "teaching_suggestions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    suggestion_type = Column(String(50), default="alert")  # alert, warning, suggestion, pedagogical_tip
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # info, warning, alert
    triggered_by = Column(String(50), default="attention_drop")

    session = relationship("SessionModel", back_populates="suggestions")


class TeacherProfileModel(Base):
    """
    Long-term teacher effectiveness profile and class history comparison.
    """
    __tablename__ = "teacher_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(String(50), unique=True, index=True, nullable=False)
    teacher_name = Column(String(100), default="Instructor")
    effectiveness_score = Column(Float, default=87.5)
    trend = Column(Float, default=12.0)
    strengths_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    class_history_json = Column(Text, nullable=True)
