"""
Newsletter Engine - Email Campaign Automation
==============================================

Generates and sends newsletters with AI content, embedded videos,
and helpful AI-related messages to customer base.

Integrates with GHL Email API for delivery.

Part of the Content Engine & Social Command Center.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Try to import Gemini
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Configuration
GHL_API_BASE = "https://services.leadconnectorhq.com"
CONTENT_LIBRARY_DIR = Path(__file__).parent.parent / "content_library"
NEWSLETTERS_DIR = CONTENT_LIBRARY_DIR / "newsletters"

# Newsletter templates
NEWSLETTER_TYPES = {
    "weekly_tips": {
        "subject_prefix": "🤖 AI Tip of the Week:",
        "sections": ["intro", "main_tip", "video_spotlight", "quick_wins", "cta"],
        "tone": "friendly and helpful"
    },
    "product_update": {
        "subject_prefix": "🚀 What's New:",
        "sections": ["headline", "features", "how_to_use", "cta"],
        "tone": "exciting and informative"
    },
    "case_study": {
        "subject_prefix": "📈 Success Story:",
        "sections": ["intro", "challenge", "solution", "results", "cta"],
        "tone": "storytelling with social proof"
    },
    "ai_news": {
        "subject_prefix": "🔮 AI Insights:",
        "sections": ["headline", "news_items", "what_it_means", "action_steps"],
        "tone": "authoritative yet accessible"
    }
}


class NewsletterEngine:
    """
    AI-powered newsletter generation and GHL email integration.
    """
    
    def __init__(
        self,
        ghl_api_key: Optional[str] = None,
        ghl_location_id: Optional[str] = None,
        gemini_key: Optional[str] = None
    ):
        """
        Initialize Newsletter Engine.
        
        Args:
            ghl_api_key: GHL API key
            ghl_location_id: GHL location ID
            gemini_key: Google Gemini API key
        """
        self.ghl_api_key = ghl_api_key or os.getenv("GHL_API_KEY")
        self.ghl_location_id = ghl_location_id or os.getenv("GHL_LOCATION_ID")
        self.gemini_key = gemini_key or os.getenv("GOOGLE_API_KEY")
        
        if self.gemini_key and GENAI_AVAILABLE:
            genai.configure(api_key=self.gemini_key)
            self.llm = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.llm = None
        
        NEWSLETTERS_DIR.mkdir(parents=True, exist_ok=True)
        self.newsletters = []
    
    def _ghl_headers(self) -> Dict[str, str]:
        """Get GHL API headers."""
        return {
            "Authorization": f"Bearer {self.ghl_api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
    
    @self_annealing
    def generate_newsletter(
        self,
        topic: str,
        newsletter_type: str = "weekly_tips",
        video_url: Optional[str] = None,
        video_thumbnail: Optional[str] = None,
        cta_link: Optional[str] = None,
        cta_text: str = "Book a Free Strategy Call"
    ) -> Dict[str, Any]:
        """
        Generate a newsletter with AI content.
        
        Args:
            topic: Main topic/theme
            newsletter_type: Type of newsletter
            video_url: Video to embed
            video_thumbnail: Thumbnail for video
            cta_link: Call-to-action link
            cta_text: CTA button text
        
        Returns:
            Generated newsletter content
        """
        if not self.llm:
            return {"success": False, "error": "Gemini not configured"}
        
        template = NEWSLETTER_TYPES.get(newsletter_type, NEWSLETTER_TYPES["weekly_tips"])
        
        prompt = f"""Write an email newsletter about: {topic}

Newsletter type: {newsletter_type}
Tone: {template['tone']}
Sections to include: {', '.join(template['sections'])}

Requirements:
- Keep it scannable with short paragraphs
- Use bullet points where appropriate
- Include 1-2 emojis per section (but don't overdo it)
- Make it personal - use "you" and "your"
- End with a clear call-to-action
- Total length: 300-400 words
- Do NOT use AI-isms like "delve", "tapestry", "landscape"

If a video is being included, reference it naturally in the content.

Output format (HTML email):
SUBJECT: [Catchy subject line]
PREVIEW: [Preview text, 50-90 characters]

[HTML content with inline styles for email compatibility]
"""
        
        try:
            response = self.llm.generate_content(prompt)
            content = response.text.strip()
            
            # Parse subject and preview
            subject = ""
            preview = ""
            html_body = content
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("PREVIEW:"):
                    preview = line.replace("PREVIEW:", "").strip()
                    html_body = '\n'.join(lines[i+1:]).strip()
                    break
            
            # Add subject prefix
            if subject and not subject.startswith(template["subject_prefix"][:2]):
                subject = f"{template['subject_prefix']} {subject}"
            
            # Embed video if provided
            if video_url:
                html_body = self._embed_video_html(html_body, video_url, video_thumbnail)
            
            # Add CTA button
            if cta_link:
                html_body = self._add_cta_button(html_body, cta_link, cta_text)
            
            # Wrap in email template
            full_html = self._wrap_email_template(html_body)
            
            newsletter = {
                "id": f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "subject": subject or f"{template['subject_prefix']} {topic}",
                "preview_text": preview,
                "html_body": full_html,
                "plain_text": self._html_to_plain(html_body),
                "type": newsletter_type,
                "topic": topic,
                "video_url": video_url,
                "cta_link": cta_link,
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            
            # Save newsletter
            newsletter_path = NEWSLETTERS_DIR / f"{newsletter['id']}.json"
            with open(newsletter_path, "w") as f:
                json.dump(newsletter, f, indent=2)
            
            self.newsletters.append(newsletter)
            
            print(f"[NEWSLETTER] ✅ Generated: {newsletter['subject']}")
            
            return {
                "success": True,
                "newsletter": newsletter,
                "path": str(newsletter_path)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _embed_video_html(
        self,
        html: str,
        video_url: str,
        thumbnail: Optional[str] = None
    ) -> str:
        """Embed video in HTML email (as clickable thumbnail)."""
        # Emails can't embed videos directly, use clickable thumbnail
        thumb = thumbnail or "https://via.placeholder.com/560x315?text=Watch+Video"
        
        video_html = f'''
<div style="text-align: center; margin: 20px 0;">
    <a href="{video_url}" target="_blank" style="display: inline-block;">
        <img src="{thumb}" alt="Watch Video" style="max-width: 100%; border-radius: 8px; border: 2px solid #e0e0e0;">
        <p style="color: #0066cc; font-size: 14px; margin-top: 8px;">▶️ Click to Watch</p>
    </a>
</div>
'''
        # Insert after first paragraph
        if '</p>' in html:
            idx = html.find('</p>') + 4
            html = html[:idx] + video_html + html[idx:]
        else:
            html = video_html + html
        
        return html
    
    def _add_cta_button(self, html: str, link: str, text: str) -> str:
        """Add CTA button to email."""
        cta_html = f'''
<div style="text-align: center; margin: 30px 0;">
    <a href="{link}" target="_blank" style="
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 28px;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
    ">{text}</a>
</div>
'''
        return html + cta_html
    
    def _wrap_email_template(self, body: str) -> str:
        """Wrap content in responsive email template."""
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px;">
        {body}
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
        <p style="color: #888; font-size: 12px; text-align: center;">
            You're receiving this because you subscribed to our updates.<br>
            <a href="{{{{unsubscribe_link}}}}" style="color: #888;">Unsubscribe</a>
        </p>
    </div>
</body>
</html>'''
    
    def _html_to_plain(self, html: str) -> str:
        """Convert HTML to plain text."""
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @self_annealing
    def send_via_ghl(
        self,
        newsletter_id: str,
        contact_list: Optional[str] = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Send newsletter via GHL Email API.
        
        Args:
            newsletter_id: Newsletter ID to send
            contact_list: GHL contact list/tag to send to
            schedule_time: Optional scheduled send time
        
        Returns:
            Send status
        """
        if not self.ghl_api_key:
            return {"success": False, "error": "GHL API not configured"}
        
        # Load newsletter
        newsletter = self._load_newsletter(newsletter_id)
        if not newsletter:
            return {"success": False, "error": "Newsletter not found"}
        
        try:
            # Create email campaign in GHL
            payload = {
                "locationId": self.ghl_location_id,
                "name": newsletter["subject"],
                "status": "scheduled" if schedule_time else "active",
                "emailSubject": newsletter["subject"],
                "previewText": newsletter.get("preview_text", ""),
                "htmlBody": newsletter["html_body"],
            }
            
            if schedule_time:
                payload["scheduledAt"] = schedule_time.isoformat()
            
            response = requests.post(
                f"{GHL_API_BASE}/emails/campaigns",
                headers=self._ghl_headers(),
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                # Update newsletter status
                newsletter["status"] = "sent"
                newsletter["sent_at"] = datetime.now().isoformat()
                newsletter["campaign_id"] = result.get("id")
                self._save_newsletter(newsletter)
                
                return {
                    "success": True,
                    "campaign_id": result.get("id"),
                    "message": "Newsletter sent/scheduled via GHL"
                }
            else:
                return {
                    "success": False,
                    "error": f"GHL API error: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_newsletter(self, newsletter_id: str) -> Optional[Dict]:
        """Load newsletter by ID."""
        path = NEWSLETTERS_DIR / f"{newsletter_id}.json"
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return None
    
    def _save_newsletter(self, newsletter: Dict):
        """Save newsletter."""
        path = NEWSLETTERS_DIR / f"{newsletter['id']}.json"
        with open(path, "w") as f:
            json.dump(newsletter, f, indent=2)
    
    def list_newsletters(self, status: Optional[str] = None) -> List[Dict]:
        """List all newsletters."""
        newsletters = []
        for path in NEWSLETTERS_DIR.glob("*.json"):
            with open(path, "r") as f:
                nl = json.load(f)
                if status is None or nl.get("status") == status:
                    newsletters.append(nl)
        return newsletters
    
    @self_annealing
    def create_drip_sequence(
        self,
        theme: str,
        num_emails: int = 5,
        days_between: int = 3
    ) -> Dict[str, Any]:
        """
        Create an automated drip email sequence.
        
        Args:
            theme: Overall theme for the sequence
            num_emails: Number of emails in sequence
            days_between: Days between each email
        
        Returns:
            Sequence of newsletters
        """
        if not self.llm:
            return {"success": False, "error": "Gemini not configured"}
        
        # Generate email topics
        topic_prompt = f"""Create a {num_emails}-email nurture sequence about: {theme}

Each email should build on the previous one and guide the reader toward booking a call.
Return as a numbered list with email subjects and brief descriptions.
"""
        
        try:
            response = self.llm.generate_content(topic_prompt)
            topics = response.text.strip().split('\n')
            
            sequence = {
                "id": f"sequence_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "theme": theme,
                "emails": []
            }
            
            types = list(NEWSLETTER_TYPES.keys())
            
            for i, topic_line in enumerate(topics[:num_emails]):
                topic = topic_line.strip().lstrip("0123456789.)-")
                if not topic:
                    continue
                
                nl_type = types[i % len(types)]
                result = self.generate_newsletter(
                    topic=topic,
                    newsletter_type=nl_type
                )
                
                if result.get("success"):
                    email = result["newsletter"]
                    email["sequence_day"] = i * days_between
                    sequence["emails"].append(email)
            
            # Save sequence
            seq_path = NEWSLETTERS_DIR / f"{sequence['id']}.json"
            with open(seq_path, "w") as f:
                json.dump(sequence, f, indent=2)
            
            return {
                "success": True,
                "sequence": sequence,
                "email_count": len(sequence["emails"])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Convenience functions
def quick_newsletter(topic: str, video_url: Optional[str] = None) -> Dict[str, Any]:
    """Generate a quick weekly tips newsletter."""
    engine = NewsletterEngine()
    return engine.generate_newsletter(
        topic=topic,
        newsletter_type="weekly_tips",
        video_url=video_url,
        cta_link="https://link.aiserviceco.com/discovery"
    )


if __name__ == "__main__":
    print("[NEWSLETTER] Newsletter Engine - Email Campaigns")
    print("=" * 55)
    
    ghl_key = os.getenv("GHL_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    
    print()
    print("Configuration Status:")
    print(f"  GHL: {'✅' if ghl_key else '⚠️ Not set'}")
    print(f"  Gemini: {'✅' if gemini_key else '⚠️ Not set'}")
    
    print()
    print("[NEWSLETTER] Available types:")
    for name, config in NEWSLETTER_TYPES.items():
        print(f"  - {name}: {config['subject_prefix']}")
    
    print(f"\n[NEWSLETTER] Newsletters dir: {NEWSLETTERS_DIR}")
    
    engine = NewsletterEngine()
    newsletters = engine.list_newsletters()
    print(f"[NEWSLETTER] Existing newsletters: {len(newsletters)}")
