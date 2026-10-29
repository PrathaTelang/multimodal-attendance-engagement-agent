"""
Activity 6.3: Validation of Multimodal Fusion and Engagement Scoring Logic.
Tests multimodal correlation, explainable formula weighting, and AI reasoning.
"""

import unittest
from backend.core.engagement_scoring import EngagementScorer
from backend.core.fusion_engine import MultimodalFusionEngine
from backend.core.ai_suggestions import AISuggestionEngine


class TestMultimodalModule(unittest.TestCase):
    def setUp(self):
        self.scorer = EngagementScorer()
        self.fusion_engine = MultimodalFusionEngine()
        self.ai_engine = AISuggestionEngine()

    def test_engagement_scoring_attentive(self):
        """Attentive student looking forward with moderate motion in attentive silence."""
        track_data = {
            'head_pose': 'forward',
            'attention_cue': 0.95,
            'movement_speed': 5.0,
            'inactivity_seconds': 0.0,
            'is_inactive': False
        }
        acoustic_context = {
            'db_level': -45.0,
            'speech_ratio': 0.1,
            'acoustic_state': 'attentive_silence'
        }
        res = self.scorer.compute_individual_score(track_data, acoustic_context)
        
        self.assertGreaterEqual(res["engagement_score"], 80.0)
        self.assertIn(res["emotion"], ["focused", "engaged"])

    def test_engagement_scoring_distracted(self):
        """Distracted student looking down for prolonged duration."""
        track_data = {
            'head_pose': 'looking_down',
            'attention_cue': 0.35,
            'movement_speed': 0.0,
            'inactivity_seconds': 18.0,
            'is_inactive': True
        }
        acoustic_context = {
            'db_level': -45.0,
            'speech_ratio': 0.0,
            'acoustic_state': 'attentive_silence'
        }
        res = self.scorer.compute_individual_score(track_data, acoustic_context)

        self.assertLessEqual(res["engagement_score"], 60.0)
        self.assertIn(res["emotion"], ["distracted", "drowsy", "neutral"])

    def test_multimodal_fusion(self):
        """Verifies timestamp-synchronized fusion snapshot structure."""
        vision_tracks = {
            1: {'bbox': (50, 50, 40, 40), 'head_pose': 'forward', 'attention_cue': 0.9, 'movement_speed': 3.0}
        }
        audio_metrics = {
            'db_level': -40.0,
            'speech_ratio': 0.25,
            'is_speech': True,
            'acoustic_state': 'instructor_speech'
        }

        fused = self.fusion_engine.fuse(vision_tracks, audio_metrics, session_id=1)
        
        self.assertIn("vision", fused)
        self.assertIn("audio", fused)
        self.assertIn("aggregate", fused)
        self.assertEqual(fused["vision"]["active_participants"], 1)

    def test_offline_ai_teaching_suggestions(self):
        """Validates AI suggestion generator under offline condition."""
        mock_session_data = {
            "aggregate": {"avg_attention": 45.0, "avg_engagement": 50.0, "status": "Low Engagement Alert"},
            "audio": {"db_level": -45.0, "speech_ratio": 0.1, "acoustic_state": "attentive_silence"},
            "vision": {"inactivity_count": 2, "looking_down_count": 2}
        }
        insight = self.ai_engine.generate_classroom_insight(mock_session_data)
        
        self.assertIn("insight", insight)
        self.assertIn("recommendation", insight)
        self.assertTrue(len(insight["recommendation"]) > 10)


if __name__ == "__main__":
    unittest.main()
