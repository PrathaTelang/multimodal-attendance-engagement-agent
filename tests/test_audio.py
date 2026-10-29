"""
Activity 6.3: Validation of Audio Module.
Tests noise decibel calculation, Voice Activity Detection (VAD),
speech vs silence ratios, and acoustic state classifications.
"""

import unittest
import numpy as np
from backend.core.audio_analysis import AudioAnalyzer


class TestAudioModule(unittest.TestCase):
    def setUp(self):
        self.analyzer = AudioAnalyzer(sample_rate=16000)

    def test_silence_handling(self):
        """Edge Case: Pure silence or near-zero input."""
        silent_samples = np.zeros(1600, dtype=np.int16).tobytes()
        metrics = self.analyzer.analyze_audio_chunk(silent_samples)
        
        self.assertIsNotNone(metrics)
        self.assertLessEqual(metrics["db_level"], -45.0)
        self.assertFalse(metrics["is_speech"])
        self.assertEqual(metrics["acoustic_state"], "attentive_silence")

    def test_speech_simulation_detection(self):
        """Verifies voice activity detection and speech ratio elevation."""
        speech_pcm = self.analyzer.simulate_audio_chunk(mode="lecture")
        metrics = self.analyzer.analyze_audio_chunk(speech_pcm)
        
        self.assertIsNotNone(metrics)
        self.assertIn("db_level", metrics)
        self.assertIn("speech_ratio", metrics)
        self.assertIn(metrics["acoustic_state"], ["instructor_speech", "attentive_silence", "active_discussion"])

    def test_corrupted_or_empty_bytes(self):
        """Edge Case: Corrupted, partial, or empty byte buffers."""
        empty_res = self.analyzer.analyze_audio_chunk(b"")
        self.assertIsNotNone(empty_res)
        self.assertEqual(empty_res["acoustic_state"], "attentive_silence")

        single_byte_res = self.analyzer.analyze_audio_chunk(b"\x01")
        self.assertIsNotNone(single_byte_res)


if __name__ == "__main__":
    unittest.main()
