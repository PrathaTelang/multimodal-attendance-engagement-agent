"""
Activity 6.3: Validation of Vision Module and Sustained-Presence Attendance Logic.
Tests single-frame rejection (false positive mitigation), continuous presence accumulation,
and head pose / gaze attention estimations.
"""

import unittest
import numpy as np
import time
from backend.core.face_detection import FaceDetector, CentroidTracker
from backend.core.face_recognition import FaceRecognizer


class TestVisionModule(unittest.TestCase):
    def setUp(self):
        self.detector = FaceDetector()
        self.tracker = CentroidTracker(max_disappeared=5, max_distance=100)
        self.recognizer = FaceRecognizer(min_presence_seconds=5.0)

    def test_empty_or_dark_frame_handling(self):
        """Edge Case 1: Dark or blank frames should return empty detections gracefully without crash."""
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = self.detector.process_frame(blank_frame)
        self.assertIsInstance(detections, list)
        self.assertEqual(len(detections), 0)

        # None frame
        none_detections = self.detector.process_frame(None)
        self.assertEqual(none_detections, [])

    def test_centroid_tracking_association(self):
        """Verifies stable tracking ID across consecutive frames."""
        # Frame 1: Detection at (100, 100)
        det1 = [{'bbox': (80, 80, 40, 40), 'center': (100, 100), 'score': 1.0, 'head_pose': 'forward', 'attention_cue': 0.9}]
        tracks1 = self.tracker.update(det1, dt=0.033)
        self.assertEqual(len(tracks1), 1)
        obj_id = list(tracks1.keys())[0]

        # Frame 2: Slight movement to (104, 102)
        det2 = [{'bbox': (84, 82, 40, 40), 'center': (104, 102), 'score': 1.0, 'head_pose': 'forward', 'attention_cue': 0.9}]
        tracks2 = self.tracker.update(det2, dt=0.033)
        self.assertEqual(len(tracks2), 1)
        self.assertIn(obj_id, tracks2, "Centroid tracker should retain object ID across nearby displacement")

    def test_sustained_presence_attendance_logic(self):
        """
        Scenario 1 Validation:
        Single-frame / short appearances MUST NOT mark attendance as 'Present'.
        Only sustained presence >= min_presence_seconds marks attendance.
        """
        self.recognizer.reset_session()

        # Step 1: Simulate single brief appearance (2 frames, ~0.1 sec)
        mock_tracks = {1: {'bbox': (100, 100, 50, 50), 'attention_cue': 0.85}}
        self.recognizer.update_presence(mock_tracks, dt=0.1)

        records = self.recognizer.get_attendance_records()
        student_1_rec = next(r for r in records if r["person_id"] == "Student_1")
        
        # Brief appearance must be 'Pending' or 'Partial', NEVER 'Present'
        self.assertNotEqual(student_1_rec["attendance_status"], "Present")
        self.assertFalse(student_1_rec["sustained_presence_verified"])

        # Step 2: Accumulate presence to exceed 5.0 seconds threshold
        for _ in range(55):
            self.recognizer.update_presence(mock_tracks, dt=0.1)

        records_after = self.recognizer.get_attendance_records()
        student_1_rec_after = next(r for r in records_after if r["person_id"] == "Student_1")

        self.assertEqual(student_1_rec_after["attendance_status"], "Present")
        self.assertTrue(student_1_rec_after["sustained_presence_verified"])
        self.assertGreaterEqual(student_1_rec_after["presence_duration_seconds"], 5.0)


if __name__ == "__main__":
    unittest.main()
