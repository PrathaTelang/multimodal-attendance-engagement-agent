"""
Activity 4.1 & 5.1: AI Suggestion Engine.
Provides context-aware teaching suggestions based on multimodal dynamics.
Supports offline rule-based reasoning by default, with optional Groq / Gemini API integration.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


class AISuggestionEngine:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        
        # Try initializing Groq client if key is present
        if self.groq_api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
                print("[AISuggestionEngine] Initialized Groq cloud client.")
            except Exception as e:
                print(f"[AISuggestionEngine] Groq init notice (operating offline): {e}")

    def generate_classroom_insight(self, session_data: dict) -> dict:
        """
        Generates teaching suggestions and classroom dynamics insights.
        session_data: dictionary containing aggregate metrics, visual attention, audio status.
        """
        # If cloud client is available, attempt LLM call
        if self.client:
            try:
                prompt = self._build_prompt(session_data)
                completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert pedagogical AI teaching assistant. Provide brief, "
                                "professional, non-prescriptive, and actionable classroom suggestions. "
                                "Return JSON with keys: 'insight' and 'recommendation'."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.4,
                    max_tokens=150,
                    response_format={"type": "json_object"}
                )
                content = completion.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                print(f"[AISuggestionEngine] LLM fallback triggered ({e}). Using offline reasoning.")

        # Offline Intelligent Rule-Based Engine (Guaranteed zero-cloud, privacy-preserving)
        return self._offline_reasoning(session_data)

    def _build_prompt(self, session_data: dict) -> str:
        agg = session_data.get("aggregate", {})
        audio = session_data.get("audio", {})
        vision = session_data.get("vision", {})
        
        return (
            f"Classroom Status:\n"
            f"- Average Attention: {agg.get('avg_attention', 75)}%\n"
            f"- Average Engagement: {agg.get('avg_engagement', 75)}%\n"
            f"- Inactive/Sleeping Count: {vision.get('inactivity_count', 0)}\n"
            f"- Head Down Count: {vision.get('looking_down_count', 0)}\n"
            f"- Ambient Sound Level: {audio.get('db_level', -45)} dB\n"
            f"- Speech Ratio: {audio.get('speech_ratio', 0.1)}\n"
            f"- Acoustic State: {audio.get('acoustic_state', 'attentive_silence')}\n"
            f"Provide one concise insight and one actionable teaching suggestion."
        )

    def _offline_reasoning(self, session_data: dict) -> dict:
        """
        Robust, rule-based decision support logic designed for privacy-preserving offline operation.
        """
        agg = session_data.get("aggregate", {})
        audio = session_data.get("audio", {})
        vision = session_data.get("vision", {})

        avg_attn = agg.get("avg_attention", 75.0)
        avg_eng = agg.get("avg_engagement", 75.0)
        inactive = vision.get("inactivity_count", 0)
        looking_down = vision.get("looking_down_count", 0)
        speech_ratio = audio.get("speech_ratio", 0.1)
        db_level = audio.get("db_level", -45.0)

        # Context evaluation
        if avg_attn < 55.0 or looking_down >= 2:
            return {
                "insight": "Attention drop detected across multiple participants.",
                "recommendation": "Launch a quick 60-second interactive poll or check-in prompt (+18% focus recovery).",
                "status": "attention_dip"
            }
        elif inactive >= 1:
            return {
                "insight": f"Detected prolonged physical stagnation for {inactive} learner(s).",
                "recommendation": "Incorporate a brief open question or pair-share discussion to reactivate learner focus.",
                "status": "inactivity_alert"
            }
        elif db_level > -28.0 and speech_ratio < 0.2:
            return {
                "insight": "Elevated ambient background noise without structured speech.",
                "recommendation": "Pause briefly for classroom refocusing or verify audio microphone positioning.",
                "status": "noise_alert"
            }
        elif speech_ratio > 0.60:
            return {
                "insight": "High verbal interaction observed. Session dynamics are lively and participative.",
                "recommendation": "Summarize student contributions on the board before transitioning to the next concept.",
                "status": "collaborative_peak"
            }
        elif avg_eng >= 85.0:
            return {
                "insight": "Classroom engagement is optimal. High visual attentiveness and synchronized pacing.",
                "recommendation": "Maintain current lecture pacing; ideal time to introduce complex core principles.",
                "status": "optimal"
            }
        else:
            return {
                "insight": "Session progression is steady with balanced attentiveness.",
                "recommendation": "Consider pausing at the 20-minute mark for a quick comprehension check.",
                "status": "steady"
            }
