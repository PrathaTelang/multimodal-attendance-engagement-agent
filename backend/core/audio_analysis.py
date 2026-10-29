"""
Milestone 3: Audio Signal Extraction & Noise/Speech Activity Analysis (Activities 3.1 & 3.2).
Analyzes ambient noise levels (dB), voice activity detection (VAD),
speech vs silence ratios, and acoustic interaction patterns.
Operates completely offline with zero external cloud dependencies.
"""

import numpy as np
import time
from collections import deque


class AudioAnalyzer:
    def __init__(self, sample_rate=16000, frame_duration_ms=30):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        
        # Rolling history of audio metrics for temporal aggregation
        self.history_len = 50  # ~5 seconds of 100ms chunks
        self.db_history = deque(maxlen=self.history_len)
        self.speech_flags = deque(maxlen=self.history_len)
        
        # Calibrated baseline noise threshold (dB)
        self.silence_threshold_db = -50.0
        self.speech_threshold_db = -38.0

    def analyze_audio_chunk(self, audio_data):
        """
        Analyzes a chunk of audio (raw 16-bit PCM bytes or float32 numpy array).
        Returns dictionary containing:
        - rms_energy: Root mean square energy
        - db_level: Ambient sound level in decibels (-90 dB to 0 dB)
        - is_speech: Boolean voice activity detection (VAD)
        - speech_ratio: Rolling percentage of time speech was detected
        - acoustic_state: 'attentive_silence', 'active_discussion', 'instructor_speech', 'elevated_noise'
        """
        try:
            if isinstance(audio_data, (bytes, bytearray)):
                if len(audio_data) < 2:
                    return self._get_fallback_metrics()
                # 16-bit PCM little endian
                y = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            elif isinstance(audio_data, np.ndarray):
                y = audio_data.astype(np.float32)
                if y.max() > 1.0 or y.min() < -1.0:
                    y = y / 32768.0
            else:
                return self._get_fallback_metrics()

            if len(y) == 0:
                return self._get_fallback_metrics()

            # 1. RMS Energy
            rms = np.sqrt(np.mean(y ** 2) + 1e-12)
            
            # 2. Decibel calculation (dBFS, 0 dBFS is full-scale sine wave)
            db = 20.0 * np.log10(rms + 1e-9)
            db = float(np.clip(db, -90.0, 0.0))
            self.db_history.append(db)

            # 3. Zero Crossing Rate (ZCR) - distinguishes voiced speech from white noise
            zero_crossings = np.sum(np.abs(np.diff(y > 0))) / max(len(y) - 1, 1)

            # 4. Voice Activity Detection (VAD)
            # Voiced speech typically has moderate-high energy and specific ZCR range (0.02 - 0.25)
            is_speech = (db > self.speech_threshold_db) and (0.015 < zero_crossings < 0.35)
            self.speech_flags.append(1 if is_speech else 0)

            # 5. Speech vs Silence Ratio
            speech_ratio = float(sum(self.speech_flags) / max(len(self.speech_flags), 1))
            avg_recent_db = float(np.mean(self.db_history)) if self.db_history else db

            # 6. Acoustic State Classification
            if speech_ratio > 0.65 and avg_recent_db > -28.0:
                acoustic_state = "active_discussion"
            elif speech_ratio > 0.30:
                acoustic_state = "instructor_speech"
            elif avg_recent_db > -32.0 and speech_ratio < 0.15:
                acoustic_state = "elevated_noise"
            else:
                acoustic_state = "attentive_silence"

            return {
                "timestamp": time.time(),
                "rms_energy": round(float(rms), 5),
                "db_level": round(db, 1),
                "avg_db": round(avg_recent_db, 1),
                "zero_crossing_rate": round(float(zero_crossings), 4),
                "is_speech": bool(is_speech),
                "speech_ratio": round(speech_ratio, 2),
                "acoustic_state": acoustic_state
            }

        except Exception as e:
            print(f"[AudioAnalyzer] Error analyzing audio chunk: {e}")
            return self._get_fallback_metrics()

    def _get_fallback_metrics(self):
        """Returns baseline quiet classroom metrics."""
        return {
            "timestamp": time.time(),
            "rms_energy": 0.005,
            "db_level": -48.0,
            "avg_db": -48.0,
            "zero_crossing_rate": 0.05,
            "is_speech": False,
            "speech_ratio": 0.05,
            "acoustic_state": "attentive_silence"
        }

    def simulate_audio_chunk(self, mode="lecture"):
        """
        Generates synthetic 16-bit PCM audio samples for testing or demo without microphone.
        Modes: 'lecture', 'discussion', 'quiet_work', 'noisy'.
        """
        samples_count = int(self.sample_rate * 0.1)  # 100ms
        t = np.linspace(0, 0.1, samples_count, endpoint=False)
        
        if mode == "lecture":
            # Instructor speaking periodically
            speech_signal = 0.25 * np.sin(2 * np.pi * 180 * t) + 0.15 * np.sin(2 * np.pi * 320 * t)
            noise = np.random.normal(0, 0.015, samples_count)
            signal = speech_signal + noise
        elif mode == "discussion":
            # Higher energy multi-harmonic speech
            speech_signal = (0.35 * np.sin(2 * np.pi * 220 * t) +
                             0.25 * np.sin(2 * np.pi * 440 * t) +
                             0.15 * np.sin(2 * np.pi * 660 * t))
            noise = np.random.normal(0, 0.03, samples_count)
            signal = speech_signal + noise
        elif mode == "noisy":
            # Background shuffling, rumbling noise
            noise = np.random.normal(0, 0.12, samples_count)
            signal = noise
        else:
            # Quiet classroom
            noise = np.random.normal(0, 0.005, samples_count)
            signal = noise

        # Scale to 16-bit PCM integer bytes
        pcm_data = (np.clip(signal, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
        return pcm_data
