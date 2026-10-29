"""
Activity 5.1: Recommendations Engine.
Generates immediate rule-based alerts and pedagogical interventions.
Implements the exact logic specified in Project Specification (Pages 32-33).
"""

from typing import List, Dict, Any


class RecommendationsEngine:
    def __init__(self, low_attention_threshold=40.0, global_attention_threshold=60.0):
        self.low_attention_threshold = low_attention_threshold
        self.global_attention_threshold = global_attention_threshold

    def generate_realtime_recommendations(self, session_status: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Rule-based recommendations for immediate feedback.
        Input: session status dict (people, emotions, attention, audio)
        Output: list of dicts with 'type' ('alert' | 'warning' | 'info') and 'message'
        """
        recs = []
        people = session_status.get('people', [])
        audio_info = session_status.get('audio', {})

        if people:
            # Calculate aggregate attention across all active participants
            avg_att = sum(p.get('attention', 70.0) for p in people) / max(len(people), 1)

            # 1. Individual Attention Checks
            for p in people:
                p_id = p.get('id', p.get('person_id', 'Unknown'))
                p_att = p.get('attention', 70.0)
                p_inact = p.get('inactivity_seconds', 0.0)
                
                if p_att < self.low_attention_threshold:
                    recs.append({
                        'type': 'alert',
                        'severity': 'high',
                        'message': f"Student {p_id} is distracted ({int(p_att)}% attention)."
                    })
                elif p_inact > 12.0:
                    recs.append({
                        'type': 'warning',
                        'severity': 'medium',
                        'message': f"Student {p_id} has been physically inactive for {int(p_inact)}s."
                    })

            # 2. Global Attention Warning
            if len(people) >= 1 and avg_att < self.global_attention_threshold:
                recs.append({
                    'type': 'warning',
                    'severity': 'high',
                    'message': f"Low attention across class ({int(avg_att)}% < 60%). Interactive break recommended."
                })
            elif avg_att >= 85.0:
                recs.append({
                    'type': 'info',
                    'severity': 'low',
                    'message': "High class attentiveness (85%+). Excellent lecture receptivity."
                })

        # 3. Acoustic Checks
        db = audio_info.get('db_level', -45.0)
        state = audio_info.get('acoustic_state', 'attentive_silence')
        
        if db > -26.0 and state == "elevated_noise":
            recs.append({
                'type': 'alert',
                'severity': 'medium',
                'message': f"Elevated ambient noise detected ({db} dB). Classroom management check advised."
            })
        elif state == "active_discussion":
            recs.append({
                'type': 'info',
                'severity': 'low',
                'message': "Collaborative discussion detected. Allow students 2 minutes to summarize."
            })

        return recs
