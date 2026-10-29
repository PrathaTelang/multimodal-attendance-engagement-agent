"""
Activity 4.3: Engagement Scoring Logic.
Transforms fused multimodal signals into transparent, interpretable engagement scores.
Calculates individual and aggregate classroom engagement metrics across sliding time segments.
"""

import numpy as np


class EngagementScorer:
    """
    Explainable multimodal engagement scoring engine.
    Computes individual attention scores and session-level engagement indexes.
    Weights:
      - Visual Attention (Head Pose & Gaze Proxy): 45%
      - Motion Dynamics & Inactivity Penalty: 25%
      - Acoustic Context & Interaction Factor: 30%
    """
    def __init__(self,
                 weight_visual=0.45,
                 weight_motion=0.25,
                 weight_acoustic=0.30):
        self.w_visual = weight_visual
        self.w_motion = weight_motion
        self.w_acoustic = weight_acoustic

    def compute_individual_score(self, track_data, acoustic_context):
        """
        Computes real-time engagement score (0-100) for a single tracked participant.
        track_data: { head_pose, attention_cue, movement_speed, inactivity_seconds, is_inactive }
        acoustic_context: { db_level, speech_ratio, acoustic_state }
        """
        # 1. Visual Attention Component (0.0 to 1.0)
        # Head pose forward gives highest score; turned away or down reduces score
        head_pose = track_data.get('head_pose', 'forward')
        base_visual = track_data.get('attention_cue', 0.8)
        
        if head_pose == "forward":
            visual_score = base_visual * 100.0
        elif head_pose == "turned_away":
            visual_score = base_visual * 75.0
        else:  # looking down (often phone/laptop or drowsy)
            visual_score = base_visual * 50.0

        # 2. Motion Dynamics Component (0.0 to 100.0)
        # Moderate natural movement indicates active engagement.
        # Prolonged stagnation (inactivity > 10s) indicates lack of interaction or sleeping.
        # Excessive erratic speed indicates disruption.
        speed = track_data.get('movement_speed', 0.0)
        inactivity_sec = track_data.get('inactivity_seconds', 0.0)
        
        if inactivity_sec > 15.0:
            motion_score = max(20.0, 70.0 - (inactivity_sec - 15.0) * 3.0)
        elif 1.0 <= speed <= 25.0:
            # Active responsive posture
            motion_score = 90.0
        elif speed > 50.0:
            # Sudden high erratic movement
            motion_score = 65.0
        else:
            motion_score = 75.0

        # 3. Acoustic Context Modulation (0.0 to 100.0)
        acoustic_state = acoustic_context.get('acoustic_state', 'attentive_silence')
        speech_ratio = acoustic_context.get('speech_ratio', 0.1)

        if acoustic_state == "attentive_silence":
            # Classroom is quiet; visual focus is rewarded
            acoustic_factor = 85.0
        elif acoustic_state == "active_discussion":
            # Active collaborative discussion; speech is rewarded
            acoustic_factor = 95.0
        elif acoustic_state == "instructor_speech":
            # Standard lecture cadence
            acoustic_factor = 88.0
        elif acoustic_state == "elevated_noise":
            # Background chatter / ambient distraction
            acoustic_factor = 50.0
        else:
            acoustic_factor = 70.0

        # Weighted combination
        raw_score = (self.w_visual * visual_score +
                     self.w_motion * motion_score +
                     self.w_acoustic * acoustic_factor)
        
        final_score = round(float(np.clip(raw_score, 5.0, 100.0)), 1)
        
        # Determine emotion / behavioral classification
        if final_score >= 82:
            emotion = "focused"
        elif final_score >= 68:
            emotion = "engaged"
        elif final_score >= 50:
            emotion = "neutral"
        elif inactivity_sec > 12.0:
            emotion = "drowsy"
        else:
            emotion = "distracted"

        return {
            "attention_score": round(visual_score, 1),
            "engagement_score": final_score,
            "emotion": emotion,
            "head_pose": head_pose,
            "is_inactive": track_data.get('is_inactive', False)
        }

    def compute_classroom_aggregate(self, individual_scores, acoustic_context):
        """
        Computes aggregate metrics across all active students in the session.
        """
        if not individual_scores:
            return {
                "active_count": 0,
                "avg_attention": 0.0,
                "avg_engagement": 0.0,
                "attention_drop_count": 0,
                "status": "No Participants"
            }

        attentions = [s["attention_score"] for s in individual_scores]
        engagements = [s["engagement_score"] for s in individual_scores]

        avg_attn = round(float(np.mean(attentions)), 1)
        avg_eng = round(float(np.mean(engagements)), 1)
        drops = sum(1 for a in attentions if a < 50.0)

        if avg_eng >= 80.0:
            status = "High Engagement"
        elif avg_eng >= 65.0:
            status = "Moderate Engagement"
        elif avg_eng >= 50.0:
            status = "Pacing Adjustment Needed"
        else:
            status = "Low Engagement Alert"

        return {
            "active_count": len(individual_scores),
            "avg_attention": avg_attn,
            "avg_engagement": avg_eng,
            "attention_drop_count": drops,
            "status": status,
            "acoustic_state": acoustic_context.get("acoustic_state", "attentive_silence")
        }
