"""
Activity 6.3: Validation of Recommendation Engine and Teacher Profiles.
Tests low-attention alerts, global classroom warnings, and longitudinal metrics.
"""

import unittest
from backend.database.db import init_db
from backend.core.recommendations_engine import RecommendationsEngine
from backend.core.teacher_profiles import TeacherProfileService


class TestRecommendationsAndProfiles(unittest.TestCase):
    def setUp(self):
        init_db()
        self.recs_engine = RecommendationsEngine()
        self.teacher_service = TeacherProfileService()

    def test_individual_distraction_alert(self):
        """Verifies low individual attention triggers alert."""
        session_status = {
            "people": [
                {"id": "Student_1", "attention": 32.0, "inactivity_seconds": 0.0},
                {"id": "Student_2", "attention": 85.0, "inactivity_seconds": 0.0}
            ],
            "audio": {"db_level": -45.0, "acoustic_state": "attentive_silence"}
        }
        recs = self.recs_engine.generate_realtime_recommendations(session_status)
        
        has_alert = any("distracted" in r["message"] for r in recs)
        self.assertTrue(has_alert)

    def test_global_attention_warning(self):
        """Verifies class-wide attention drop triggers warning."""
        session_status = {
            "people": [
                {"id": "Student_1", "attention": 45.0},
                {"id": "Student_2", "attention": 50.0}
            ],
            "audio": {"db_level": -45.0, "acoustic_state": "attentive_silence"}
        }
        recs = self.recs_engine.generate_realtime_recommendations(session_status)

        has_warning = any("Low attention across class" in r["message"] for r in recs)
        self.assertTrue(has_warning)

    def test_teacher_profile_retrieval(self):
        """Verifies instructor profile contains required metrics and history."""
        profile = self.teacher_service.get_profile("T_101")
        
        self.assertIn("effectiveness_score", profile)
        self.assertIn("strengths", profile)
        self.assertIn("recommendations", profile)
        self.assertIn("class_history", profile)
        self.assertGreater(profile["effectiveness_score"], 50.0)


if __name__ == "__main__":
    unittest.main()
