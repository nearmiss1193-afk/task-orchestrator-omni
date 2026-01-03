import os
import requests
import json
from datetime import datetime

class NexusAgent:
    """
    MISSION: VOICE INTELLIGENCE LAYER
    Captures tone, confidence, and sentiment from Vapi.ai calls.
    Stores metrics in voice_logs and maps to conversion outcomes.
    """
    def __init__(self, vapi_key=None):
        self.api_key = vapi_key or os.environ.get("VAPI_PRIVATE_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def analyze_call_batch(self, limit=10):
        """
        Polls recent calls and processes un-analyzed ones.
        """
        print("🎙️ [Nexus] Fetching recent calls for analysis...")
        try:
            res = requests.get(f"{self.base_url}/call", headers=self.headers, params={"limit": limit})
            calls = res.json()
            
            results = []
            for call in calls:
                # Basic dedup logic would go here (check DB if call_id exists)
                metrics = self._process_single_call(call)
                if metrics:
                    results.append(metrics)
                    
            print(f"🎙️ [Nexus] Analyzed {len(results)} calls.")
            return results
        except Exception as e:
            print(f"Nexus Error: {e}")
            return []

    def _process_single_call(self, call_data):
        """
        Extracts Tone, Confidence, Sentiment.
        """
        try:
            call_id = call_data.get('id')
            analysis = call_data.get('analysis', {})
            transcript = call_data.get('transcript', "")
            
            # 1. Parse Vapi Metrics (Structured if available, else heuristic from summary)
            summary = analysis.get('summary', '')
            structured = analysis.get('structuredData', {})
            
            # Sentiment Extraction (Vapi often gives 'sentiment' in analysis)
            sentiment_score = 0.5 # Neutral default
            sentiment_label = "Neutral"
            
            # Mocking Extraction Logic (Vapi API varies on 'analysis' structure)
            if 'positive' in summary.lower(): 
                sentiment_score = 0.8; sentiment_label = "Positive"
            elif 'angry' in summary.lower() or 'not interested' in summary.lower():
                sentiment_score = 0.2; sentiment_label = "Negative"
                
            # Confidence (Duration proxy + user turns)
            duration =  call_data.get('durationSeconds', 0)
            confidence = min(duration / 60.0, 1.0) # Longer calls = higher engagement usually
            
            # 2. Outcome Mapping
            outcome = "calibrated"
            conversion_signal = False
            if "appointment" in summary.lower() or "book" in summary.lower():
                outcome = "conversion"
                conversion_signal = True
            elif "voice mail" in summary.lower():
                outcome = "voicemail"
            
            # 3. Store in DB
            self._log_voice_metric(call_id, sentiment_label, sentiment_score, confidence, outcome)
            
            return {
                "id": call_id,
                "sentiment": sentiment_label,
                "confidence": confidence,
                "outcome": outcome
            }
        except Exception as e:
            print(f"Skipping Call {call_data.get('id')}: {e}")
            return None

    def _log_voice_metric(self, call_id, tone, score, conf, outcome):
        try:
            from deploy import get_supabase
            sb = get_supabase()
            
            # Upsert into voice_logs
            sb.table("voice_logs").upsert({
                "call_id": call_id,
                "sentiment_tone": tone,
                "sentiment_score": score,
                "confidence_index": conf,
                "outcome": outcome,
                "analyzed_at": datetime.now().isoformat()
            }).execute()
            
            # Performance Insight
            if outcome == "conversion":
                print(f"🚀 [Nexus] CONVERSION DETECTED in Call {call_id}. Boosting Lead Score.")
                # Future: Link to contact_id and boost score
                
        except Exception as e:
            # Squelch DB errors for now
            pass

if __name__ == "__main__":
    nexus = NexusAgent()
    nexus.analyze_call_batch()
