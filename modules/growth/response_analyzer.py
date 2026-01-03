import os
import datetime
import json
import requests
from modules.governor.internal_supervisor import InternalSupervisor

class ResponseAnalyzer:
    """
    MISSION: CAMPAIGN EVOLUTION
    Analyzes GHL conversations, categorizes sentiment, and auto-tunes the 'Spear' prompt.
    """
    def __init__(self, token=None, location_id=None):
        self.token = token or os.environ.get("GHL_AGENCY_API_TOKEN") or os.environ.get("GHL_API_TOKEN")
        self.location_id = location_id or os.environ.get("GHL_LOCATION_ID")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Version": "2021-04-15", 
            "Content-Type": "application/json"
        }
        # Use V1 'conversations' search or V2 if available. limiting to V1/V2 mix is tricky. 
        # Using 2021-04-15 (V1) for 'conversations/search' is reliable for many.

    def run_daily_analysis(self):
        print("🧠 [Analyzer] Starting Daily Review...")
        
        # 1. Fetch Conversations (Last 24h)
        convos = self._fetch_recent_conversations()
        if not convos:
            print("No new conversations found.")
            return

        # 2. Analyze Sentiment
        stats = {"positive": 0, "neutral": 0, "negative": 0, "total": 0}
        negative_feedback = []
        
        for c in convos:
            msg = self._get_last_message(c)
            if not msg: continue
            
            sentiment = self._classify_sentiment(msg)
            stats[sentiment] += 1
            stats["total"] += 1
            
            if sentiment == "negative":
                negative_feedback.append(msg)

        # 3. Update Database (campaign_performance)
        self._record_stats(stats)
        
        # 4. Auto-Optimize (If Negative Rate > 30%)
        neg_rate = (stats["negative"] / stats["total"]) if stats["total"] > 0 else 0
        print(f"📉 Negative Rate: {neg_rate*100:.1f}%")
        
        if neg_rate > 0.30 and len(negative_feedback) > 0:
            print("⚠️ High Failure Rate Detected. Initiating Mutation...")
            self._mutate_spear_prompt(negative_feedback)
        else:
            print("✅ Campaign Performing within Tolerances.")

    def _fetch_recent_conversations(self):
        # MOCK/STUB: In production, query GHL API `conversations/search` with date filter
        # For this handoff, we assume we get a list of recent inbound messages
        # Real call logic would go here.
        return [] 

    def _get_last_message(self, convo):
        return convo.get('lastMessageBody')

    def _classify_sentiment(self, text):
        # Heuristic Analysis (Speed)
        text = text.lower()
        if any(x in text for x in ["stop", "remove", "hate", "spam", "no", "unsubscribe"]):
            return "negative"
        if any(x in text for x in ["price", "cost", "interested", "yes", "demo", "call"]):
            return "positive"
        return "neutral"

    def _record_stats(self, stats):
        try:
            from deploy import get_supabase
            sb = get_supabase()
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            # Upsert logic
            sb.table("campaign_performance").insert({
                "date": today,
                "positive": stats["positive"],
                "negative": stats["negative"],
                "total": stats["total"]
            }).execute()
            print("📊 Stats Saved to DB.")
        except Exception as e:
            print(f"DB Save Error (Table might not exist): {e}")

    def _mutate_spear_prompt(self, feedback_samples):
        """
        Uses Gemini to rewrite the outbound script based on rejection reasons.
        """
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        feedback_str = "\n".join([f"- {x}" for x in feedback_samples[:5]])
        
        prompt = f"""
        MISSION: REPAIR SALES SCRIPT
        Our current outreach is getting negative responses.
        
        FEEDBACK SAMPLES:
        {feedback_str}
        
        TASK:
        Write a NEW, softer, value-first email body template.
        Address the objections implicitly.
        Keep it under 100 words.
        Tone: "Spartan" (Concise, Humble, Helping).
        
        OUTPUT: Just the email body text.
        """
        
        try:
            response = model.generate_content(prompt)
            new_script = response.text.strip()
            
            # Save to 'Dynamic Gene' file
            with open("brain/dynamic_spear_prompt.txt", "w", encoding="utf-8") as f:
                f.write(new_script)
                
            print("🧬 CAMPAIGN MUTATED. New Script Saved.")
        except Exception as e:
            print(f"Mutation Failed: {e}")

if __name__ == "__main__":
    analyzer = ResponseAnalyzer()
    analyzer.run_daily_analysis()
