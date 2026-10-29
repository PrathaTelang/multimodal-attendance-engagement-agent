"""
Activity 6.3: API Endpoint and Integration Validation.
Tests FastAPI REST endpoints and data export functionality.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_dashboard_html(self):
        """Verifies dashboard serves HTML successfully."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["content-type"])

    def test_session_status_endpoint(self):
        """Verifies session status JSON payload."""
        res = self.client.get("/api/session/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("session_active", data)
        self.assertIn("avg_attention", data)
        self.assertIn("audio", data)
        self.assertIn("ai_insight", data)

    def test_attendance_endpoint(self):
        """Verifies attendance records roster endpoint."""
        res = self.client.get("/api/attendance")
        self.assertEqual(res.status_code, 200)
        records = res.json()
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)

    def test_teacher_profile_endpoint(self):
        """Verifies teacher profile endpoint."""
        res = self.client.get("/api/teacher/profile?teacher_id=T_101")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("effectiveness_score", data)
        self.assertIn("class_history", data)

    def test_analytics_trends_endpoint(self):
        """Verifies session analytics time-series endpoint."""
        res = self.client.get("/api/analytics/trends")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("attention_trend", data)
        self.assertIn("emotion_distribution", data)

    def test_csv_export_endpoint(self):
        """Verifies CSV attendance report download."""
        res = self.client.get("/api/export/csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers["content-type"])
        self.assertIn("attachment", res.headers["content-disposition"])

    def test_pdf_export_endpoint(self):
        """Verifies styled HTML/PDF session report download."""
        res = self.client.get("/api/export/pdf")
        self.assertEqual(res.status_code, 200)
        self.assertIn("attachment", res.headers["content-disposition"])


if __name__ == "__main__":
    unittest.main()
