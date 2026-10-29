"""
Activity 2.2: Presence-Based Attendance Logic and Student Recognition.
Translates continuous face tracking data into robust attendance records.
Marks attendance based on sustained presence duration rather than single-frame detections,
eliminating false positives caused by brief or accidental appearances.
"""

import os
import time
import json
from datetime import datetime
import pandas as pd


class FaceRecognizer:
    def __init__(self, db_path="data/registered_students", min_presence_seconds=15.0):
        self.db_path = db_path
        self.min_presence_seconds = min_presence_seconds
        
        os.makedirs(self.db_path, exist_ok=True)
        self.student_registry = {}  # student_id -> dict of metadata
        self._load_registry()

        # Session tracking state: person_id -> presence metadata
        self.presence_tracker = {}

    def _load_registry(self):
        """Loads registered student roster from JSON if available."""
        roster_file = os.path.join(self.db_path, "roster.json")
        if os.path.exists(roster_file):
            try:
                with open(roster_file, "r") as f:
                    self.student_registry = json.load(f)
            except Exception as e:
                print(f"[FaceRecognizer] Error loading roster: {e}")
        else:
            # Seed default classroom roster
            self.student_registry = {
                "Student_1": {"name": "Priya Sharma", "roll_no": "CS2026-01", "department": "AI & DS"},
                "Student_2": {"name": "Kumar Patel", "roll_no": "CS2026-02", "department": "AI & DS"},
                "Student_3": {"name": "Asha Varma", "roll_no": "CS2026-03", "department": "AI & DS"},
                "Student_4": {"name": "Rohan Gupta", "roll_no": "CS2026-04", "department": "AI & DS"}
            }
            self.save_registry()

    def save_registry(self):
        roster_file = os.path.join(self.db_path, "roster.json")
        with open(roster_file, "w") as f:
            json.dump(self.student_registry, f, indent=2)

    def register_student(self, student_id, name, roll_no="", department=""):
        """Registers a student into the system roster."""
        self.student_registry[student_id] = {
            "name": name,
            "roll_no": roll_no,
            "department": department
        }
        self.save_registry()
        return True

    def reset_session(self):
        """Resets presence tracking state for a new session."""
        self.presence_tracker = {}

    def update_presence(self, tracked_objects, dt=0.04):
        """
        Updates cumulative presence durations from tracked participant detections.
        tracked_objects: dict of object_id -> track dict
        dt: delta time elapsed since last update.
        """
        now = datetime.utcnow()

        for obj_id, track in tracked_objects.items():
            # Map object_id to student identity (e.g. Student_1, Student_2)
            person_key = f"Student_{obj_id}"
            reg_info = self.student_registry.get(person_key, {
                "name": f"Learner {obj_id}",
                "roll_no": f"STU-{obj_id:03d}",
                "department": "Computer Science"
            })

            if person_key not in self.presence_tracker:
                self.presence_tracker[person_key] = {
                    "person_id": person_key,
                    "student_name": reg_info["name"],
                    "roll_no": reg_info.get("roll_no", ""),
                    "first_seen": now,
                    "last_seen": now,
                    "cumulative_presence": 0.0,
                    "consecutive_absent_seconds": 0.0,
                    "sustained_presence_verified": False,
                    "attendance_status": "Pending",
                    "attention_samples": []
                }

            rec = self.presence_tracker[person_key]
            rec["last_seen"] = now
            rec["cumulative_presence"] += dt
            rec["consecutive_absent_seconds"] = 0.0
            
            # Record attention cue sample
            attn = track.get("attention_cue", 0.75) * 100.0
            rec["attention_samples"].append(attn)

            # Check sustained presence rule
            if rec["cumulative_presence"] >= self.min_presence_seconds:
                rec["sustained_presence_verified"] = True
                rec["attendance_status"] = "Present"
            elif rec["cumulative_presence"] > 2.0:
                rec["attendance_status"] = "Partial"
            else:
                rec["attendance_status"] = "Pending"

        # Check for registered students who were NOT seen in this frame
        current_seen_keys = {f"Student_{oid}" for oid in tracked_objects.keys()}
        for p_key, rec in self.presence_tracker.items():
            if p_key not in current_seen_keys:
                rec["consecutive_absent_seconds"] += dt

    def get_attendance_records(self, session_id=1):
        """
        Returns structured list of attendance records with presence duration,
        status ('Present', 'Partial', 'Absent'), and attention metrics.
        """
        records = []
        all_registered = dict(self.student_registry)

        for person_id, reg_info in all_registered.items():
            if person_id in self.presence_tracker:
                rec = self.presence_tracker[person_id]
                samples = rec["attention_samples"]
                avg_attn = round(float(sum(samples) / len(samples)), 1) if samples else 0.0
                
                records.append({
                    "session_id": session_id,
                    "person_id": person_id,
                    "student_name": rec["student_name"],
                    "roll_no": rec["roll_no"],
                    "first_seen": rec["first_seen"].strftime("%H:%M:%S"),
                    "last_seen": rec["last_seen"].strftime("%H:%M:%S"),
                    "presence_duration_seconds": round(rec["cumulative_presence"], 1),
                    "sustained_presence_verified": rec["sustained_presence_verified"],
                    "attendance_status": rec["attendance_status"],
                    "avg_attention_score": avg_attn
                })
            else:
                # Registered student never seen -> Absent
                records.append({
                    "session_id": session_id,
                    "person_id": person_id,
                    "student_name": reg_info["name"],
                    "roll_no": reg_info.get("roll_no", ""),
                    "first_seen": "--",
                    "last_seen": "--",
                    "presence_duration_seconds": 0.0,
                    "sustained_presence_verified": False,
                    "attendance_status": "Absent",
                    "avg_attention_score": 0.0
                })

        return records

    def export_attendance_csv(self, file_path="data/attendance_logs/attendance.csv"):
        """Exports current attendance logs to CSV."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        records = self.get_attendance_records()
        df = pd.DataFrame(records)
        df.to_csv(file_path, index=False)
        return file_path
