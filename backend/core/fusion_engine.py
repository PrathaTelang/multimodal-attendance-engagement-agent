"""
Activity 4.2: Multimodal Signal Fusion.
Synchronizes visual tracking cues and acoustic indicators across discrete timestamp windows.
Produces fused temporal state snapshots representing unified classroom dynamics.
"""

import time
from datetime import datetime
from collections import deque
from .engagement_scoring import EngagementScorer


class MultimodalFusionEngine:
    def __init__(self, window_seconds=2.0):
        self.window_seconds = window_seconds
        self.scorer = EngagementScorer()
        
        # Buffer of timestamped snapshots
        self.history = deque(maxlen=300)  # last ~10-15 minutes of snapshots
        self.last_sync_time = time.time()

    def fuse(self, vision_tracks, audio_metrics, session_id=1):
        """
        Synchronizes vision cues and acoustic indicators.
        vision_tracks: dict of obj_id -> track dict
        audio_metrics: dict of audio indicators (rms, db_level, is_speech, speech_ratio, acoustic_state)
        Returns unified multimodal snapshot dict.
        """
        now = time.time()
        timestamp_iso = datetime.utcnow().isoformat()

        # Compute individual scores for each active track
        individual_states = []
        for obj_id, track in vision_tracks.items():
            scores = self.scorer.compute_individual_score(track, audio_metrics)
            scores["person_id"] = f"Student_{obj_id}"
            scores["bbox"] = track.get("bbox", (0, 0, 0, 0))
            scores["movement_speed"] = track.get("movement_speed", 0.0)
            individual_states.append(scores)

        # Compute session-level aggregate
        aggregate = self.scorer.compute_classroom_aggregate(individual_states, audio_metrics)

        fused_snapshot = {
            "session_id": session_id,
            "timestamp": now,
            "timestamp_iso": timestamp_iso,
            "vision": {
                "active_participants": len(individual_states),
                "inactivity_count": sum(1 for s in individual_states if s.get("is_inactive", False)),
                "looking_down_count": sum(1 for s in individual_states if s.get("head_pose") == "looking_down"),
                "students": individual_states
            },
            "audio": {
                "db_level": audio_metrics.get("db_level", -45.0),
                "speech_ratio": audio_metrics.get("speech_ratio", 0.1),
                "is_speech": audio_metrics.get("is_speech", False),
                "acoustic_state": audio_metrics.get("acoustic_state", "attentive_silence")
            },
            "aggregate": aggregate
        }

        self.history.append(fused_snapshot)
        return fused_snapshot

    def get_recent_history(self, count=50):
        """Returns recent fused snapshots for timeline charts."""
        return list(self.history)[-count:]

    def get_session_attention_trend(self):
        """Extracts simple attention curve over time for graphing."""
        points = []
        for snap in self.history:
            points.append({
                "time": snap["timestamp_iso"][11:19],
                "attention": snap["aggregate"]["avg_attention"],
                "engagement": snap["aggregate"]["avg_engagement"],
                "db": snap["audio"]["db_level"]
            })
        return points
