"""
Engagement Monitor - Social Listening & Response System
========================================================

24/7 monitoring of social media engagement:
- Poll for new comments
- Monitor DMs across platforms
- Classify intent and sentiment
- Route to Ghost Responder or human queue

Part of the Content Engine & Social Command Center.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Try to import Gemini for sentiment analysis
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Configuration
AYRSHARE_API_BASE = "https://api.ayrshare.com/api"
GHL_API_BASE = "https://services.leadconnectorhq.com"
POLL_INTERVAL_SECONDS = 300  # 5 minutes

# Intent categories
INTENT_CATEGORIES = [
    "praise",       # Positive feedback
    "complaint",    # Negative feedback
    "question",     # Asking for info
    "interest",     # Showing interest in product/service
    "spam",         # Spam/irrelevant
    "support",      # Needs customer support
    "pricing",      # Asking about pricing
    "booking",      # Wants to schedule/book
    "referral"      # Referring someone
]

# Response priorities
PRIORITY_MAP = {
    "complaint": "urgent",
    "support": "high",
    "pricing": "high",
    "booking": "high",
    "question": "normal",
    "interest": "normal",
    "praise": "low",
    "referral": "low",
    "spam": "ignore"
}


class EngagementMonitor:
    """
    Monitors and responds to social media engagement.
    """
    
    def __init__(
        self,
        ayrshare_key: Optional[str] = None,
        ghl_api_key: Optional[str] = None,
        ghl_location_id: Optional[str] = None,
        gemini_key: Optional[str] = None
    ):
        """
        Initialize Engagement Monitor.
        
        Args:
            ayrshare_key: Ayrshare API key
            ghl_api_key: GHL API key
            ghl_location_id: GHL location ID
            gemini_key: Google Gemini API key for analysis
        """
        self.ayrshare_key = ayrshare_key or os.getenv("AYRSHARE_API_KEY")
        self.ghl_api_key = ghl_api_key or os.getenv("GHL_API_KEY")
        self.ghl_location_id = ghl_location_id or os.getenv("GHL_LOCATION_ID")
        self.gemini_key = gemini_key or os.getenv("GOOGLE_API_KEY")
        
        if self.gemini_key and GENAI_AVAILABLE:
            genai.configure(api_key=self.gemini_key)
            self.llm = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.llm = None
        
        self.pending_responses = []
        self.processed_comments = set()
        self.last_poll_time = None
    
    def _ayrshare_headers(self) -> Dict[str, str]:
        """Get Ayrshare API headers."""
        return {
            "Authorization": f"Bearer {self.ayrshare_key}",
            "Content-Type": "application/json"
        }
    
    def _ghl_headers(self) -> Dict[str, str]:
        """Get GHL API headers."""
        return {
            "Authorization": f"Bearer {self.ghl_api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
    
    @self_annealing
    def analyze_message(self, text: str) -> Dict[str, Any]:
        """
        Analyze message for sentiment and intent.
        
        Args:
            text: Message content
        
        Returns:
            Analysis results
        """
        if self.llm:
            try:
                prompt = f"""Analyze this social media message and return JSON only:

Message: "{text}"

Return exactly this JSON structure:
{{
    "sentiment": "positive" | "negative" | "neutral",
    "intent": one of {INTENT_CATEGORIES},
    "priority": "urgent" | "high" | "normal" | "low" | "ignore",
    "suggested_response": "brief suggested reply",
    "requires_human": true/false
}}"""
                
                response = self.llm.generate_content(prompt)
                result_text = response.text.strip()
                
                # Extract JSON from response
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]
                
                return json.loads(result_text)
                
            except Exception as e:
                print(f"[MONITOR] Analysis error: {e}")
        
        # Fallback: Simple keyword-based analysis
        text_lower = text.lower()
        
        sentiment = "neutral"
        if any(word in text_lower for word in ["love", "great", "amazing", "thank", "awesome"]):
            sentiment = "positive"
        elif any(word in text_lower for word in ["hate", "terrible", "awful", "worst", "refund"]):
            sentiment = "negative"
        
        intent = "question"
        if "?" in text:
            intent = "question"
        elif any(word in text_lower for word in ["price", "cost", "how much"]):
            intent = "pricing"
        elif any(word in text_lower for word in ["book", "schedule", "appointment"]):
            intent = "booking"
        elif any(word in text_lower for word in ["problem", "issue", "help", "support"]):
            intent = "support"
        elif sentiment == "positive":
            intent = "praise"
        elif sentiment == "negative":
            intent = "complaint"
        
        return {
            "sentiment": sentiment,
            "intent": intent,
            "priority": PRIORITY_MAP.get(intent, "normal"),
            "suggested_response": None,
            "requires_human": intent in ["complaint", "support"]
        }
    
    @self_annealing
    def fetch_comments_ayrshare(self, since_hours: int = 24) -> List[Dict]:
        """
        Fetch recent comments from Ayrshare.
        
        Args:
            since_hours: Look back this many hours
        
        Returns:
            List of comments
        """
        if not self.ayrshare_key:
            return []
        
        comments = []
        
        try:
            # Get recent posts
            posts_response = requests.get(
                f"{AYRSHARE_API_BASE}/history",
                headers=self._ayrshare_headers(),
                params={"lastDays": 7}
            )
            
            if posts_response.status_code == 200:
                posts = posts_response.json()
                
                for post in posts:
                    post_id = post.get("id")
                    
                    # Get comments for each post
                    comments_response = requests.get(
                        f"{AYRSHARE_API_BASE}/comments",
                        headers=self._ayrshare_headers(),
                        params={"id": post_id}
                    )
                    
                    if comments_response.status_code == 200:
                        post_comments = comments_response.json()
                        for comment in post_comments:
                            comment["post_id"] = post_id
                            comments.append(comment)
                    
                    time.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            print(f"[MONITOR] Error fetching Ayrshare comments: {e}")
        
        return comments
    
    @self_annealing
    def fetch_ghl_conversations(self, since_hours: int = 24) -> List[Dict]:
        """
        Fetch recent GHL conversations.
        
        Args:
            since_hours: Look back this many hours
        
        Returns:
            List of conversations
        """
        if not self.ghl_api_key or not self.ghl_location_id:
            return []
        
        conversations = []
        since_time = datetime.now() - timedelta(hours=since_hours)
        
        try:
            response = requests.get(
                f"{GHL_API_BASE}/conversations",
                headers=self._ghl_headers(),
                params={
                    "locationId": self.ghl_location_id,
                    "status": "open",
                    "limit": 100
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                conversations = data.get("conversations", [])
                
        except Exception as e:
            print(f"[MONITOR] Error fetching GHL conversations: {e}")
        
        return conversations
    
    def process_new_engagement(self) -> Dict[str, Any]:
        """
        Poll for and process new engagement.
        
        Returns:
            Processing summary
        """
        print(f"[MONITOR] Polling for new engagement...")
        
        new_comments = []
        new_dms = []
        processed = 0
        
        # Fetch from Ayrshare
        comments = self.fetch_comments_ayrshare()
        for comment in comments:
            comment_id = comment.get("id")
            if comment_id and comment_id not in self.processed_comments:
                # Analyze the comment
                analysis = self.analyze_message(comment.get("text", ""))
                
                comment["analysis"] = analysis
                new_comments.append(comment)
                self.processed_comments.add(comment_id)
                processed += 1
                
                # Queue for response if needed
                if analysis.get("priority") != "ignore":
                    self.pending_responses.append({
                        "type": "comment",
                        "source": "ayrshare",
                        "data": comment,
                        "analysis": analysis,
                        "queued_at": datetime.now().isoformat()
                    })
        
        # Fetch from GHL
        conversations = self.fetch_ghl_conversations()
        for convo in conversations:
            # Get latest message
            last_message = convo.get("lastMessage", {})
            if last_message.get("direction") == "inbound":
                analysis = self.analyze_message(last_message.get("body", ""))
                
                convo["analysis"] = analysis
                new_dms.append(convo)
                processed += 1
                
                if analysis.get("priority") != "ignore":
                    self.pending_responses.append({
                        "type": "dm",
                        "source": "ghl",
                        "data": convo,
                        "analysis": analysis,
                        "queued_at": datetime.now().isoformat()
                    })
        
        self.last_poll_time = datetime.now()
        
        summary = {
            "poll_time": self.last_poll_time.isoformat(),
            "new_comments": len(new_comments),
            "new_dms": len(new_dms),
            "total_processed": processed,
            "pending_responses": len(self.pending_responses),
            "comments_by_priority": self._count_by_priority(new_comments),
            "dms_by_priority": self._count_by_priority(new_dms)
        }
        
        print(f"[MONITOR] Found {len(new_comments)} comments, {len(new_dms)} DMs")
        print(f"[MONITOR] Pending responses: {len(self.pending_responses)}")
        
        return summary
    
    def _count_by_priority(self, items: List[Dict]) -> Dict[str, int]:
        """Count items by priority level."""
        counts = {"urgent": 0, "high": 0, "normal": 0, "low": 0}
        for item in items:
            priority = item.get("analysis", {}).get("priority", "normal")
            if priority in counts:
                counts[priority] += 1
        return counts
    
    def get_pending_responses(
        self,
        priority: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get pending responses to process.
        
        Args:
            priority: Filter by priority (None = all)
            limit: Max items to return
        
        Returns:
            List of pending items
        """
        if priority:
            filtered = [r for r in self.pending_responses 
                       if r.get("analysis", {}).get("priority") == priority]
        else:
            filtered = self.pending_responses
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        filtered.sort(key=lambda x: priority_order.get(
            x.get("analysis", {}).get("priority", "normal"), 2
        ))
        
        return filtered[:limit]
    
    def generate_response(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate an automated response.
        
        Args:
            message: Original message
            context: Optional context (customer info, post info)
        
        Returns:
            Generated response
        """
        if not self.llm:
            return None
        
        context_str = json.dumps(context) if context else "No additional context"
        
        prompt = f"""Generate a brief, professional social media response.

Original message: "{message}"
Context: {context_str}

Requirements:
- Keep it under 280 characters
- Be friendly and helpful
- Don't use overly formal language
- Include a call to action if appropriate

Response:"""
        
        try:
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[MONITOR] Response generation error: {e}")
            return None
    
    def respond_to_comment(
        self,
        post_id: str,
        comment_id: str,
        response_text: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Send a response to a comment.
        
        Args:
            post_id: Post ID
            comment_id: Comment to reply to
            response_text: Response content
            platform: Platform name
        
        Returns:
            Response status
        """
        if not self.ayrshare_key:
            return {"success": False, "error": "Ayrshare not configured"}
        
        try:
            response = requests.post(
                f"{AYRSHARE_API_BASE}/comments",
                headers=self._ayrshare_headers(),
                json={
                    "id": post_id,
                    "platforms": [platform],
                    "comment": response_text,
                    "commentId": comment_id
                }
            )
            
            if response.status_code == 200:
                # Remove from pending
                self.pending_responses = [
                    r for r in self.pending_responses
                    if r.get("data", {}).get("id") != comment_id
                ]
                
                return {"success": True, "response": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_monitor_loop(self, duration_minutes: int = 60):
        """
        Run continuous monitoring loop.
        
        Args:
            duration_minutes: How long to run
        """
        print(f"[MONITOR] Starting monitoring loop for {duration_minutes} minutes")
        print(f"[MONITOR] Poll interval: {POLL_INTERVAL_SECONDS}s")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                summary = self.process_new_engagement()
                
                # Auto-respond to urgent items
                urgent = self.get_pending_responses(priority="urgent")
                for item in urgent:
                    if not item.get("analysis", {}).get("requires_human"):
                        # Generate and send auto-response
                        response = self.generate_response(
                            item.get("data", {}).get("text", "")
                        )
                        if response:
                            print(f"[MONITOR] Auto-responding: {response[:50]}...")
                
                # Wait for next poll
                time.sleep(POLL_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                print("[MONITOR] Stopping...")
                break
            except Exception as e:
                print(f"[MONITOR] Error in loop: {e}")
                time.sleep(60)  # Wait before retry


# Convenience function
def check_engagement() -> Dict[str, Any]:
    """Quick check for new engagement."""
    monitor = EngagementMonitor()
    return monitor.process_new_engagement()


if __name__ == "__main__":
    print("[MONITOR] Engagement Monitor - Social Listening")
    print("=" * 55)
    
    # Check configuration
    ayrshare_key = os.getenv("AYRSHARE_API_KEY")
    ghl_key = os.getenv("GHL_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    
    print()
    print("Configuration Status:")
    print(f"  Ayrshare: {'✅' if ayrshare_key else '⚠️'}")
    print(f"  GHL: {'✅' if ghl_key else '⚠️'}")
    print(f"  Gemini (analysis): {'✅' if gemini_key else '⚠️'}")
    
    print()
    print("Intent Categories:", ", ".join(INTENT_CATEGORIES))
    
    # Initialize
    monitor = EngagementMonitor()
    print()
    print(f"[MONITOR] Pending responses: {len(monitor.pending_responses)}")
