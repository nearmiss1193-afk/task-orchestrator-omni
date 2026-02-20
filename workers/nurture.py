"""
NURTURE ENGINE v1.0
==================
Long-term drip nurture with timezone-aware outreach hours.
Handles: email drip, SMS follow-ups, call scheduling, weekly newsletter, opt-out.

Called by: system_orchestrator CRON (every 5 min)
"""
import os
import json
import requests
from datetime import datetime, timezone, timedelta


# ============================================================
#  TIMEZONE MAP: State → UTC offset (standard time)
#  For DST-aware regions, we add 1h during Mar-Nov
# ============================================================
STATE_TZ_OFFSETS = {
    # Eastern (UTC-5)
    "FL": -5, "GA": -5, "SC": -5, "NC": -5, "VA": -5, "MD": -5,
    "DE": -5, "NJ": -5, "PA": -5, "NY": -5, "CT": -5, "RI": -5,
    "MA": -5, "VT": -5, "NH": -5, "ME": -5, "OH": -5, "MI": -5,
    "IN": -5, "WV": -5, "KY": -5, "TN": -5,
    # Central (UTC-6)
    "IL": -6, "WI": -6, "MN": -6, "IA": -6, "MO": -6, "AR": -6,
    "LA": -6, "MS": -6, "AL": -6, "TX": -6, "OK": -6, "KS": -6,
    "NE": -6, "SD": -6, "ND": -6,
    # Mountain (UTC-7)
    "CO": -7, "NM": -7, "UT": -7, "MT": -7, "WY": -7, "ID": -7,
    "AZ": -7,  # AZ doesn't do DST
    # Pacific (UTC-8)
    "CA": -8, "OR": -8, "WA": -8, "NV": -8,
}

# DST: March second Sunday → November first Sunday (approx Mar 10 - Nov 3)
NO_DST_STATES = {"AZ"}  # Arizona doesn't observe DST


def _detect_state(lead: dict) -> str:
    """Extract state abbreviation from lead's raw_research or city field."""
    # Try raw_research first
    try:
        rr = json.loads(lead.get("raw_research", "{}") or "{}")
        search_query = rr.get("search_query", "") or rr.get("location", "")
        for st in STATE_TZ_OFFSETS:
            if f" {st}" in search_query or search_query.endswith(f" {st}"):
                return st
    except:
        pass
    
    # Try lead_source
    ls = (lead.get("lead_source", "") or "").lower()
    if "florida" in ls: return "FL"
    if "mountain" in ls:
        # Default to CO for mountain
        return "CO"
    if "west_coast" in ls:
        return "CA"
    
    return "FL"  # Default to Florida


def _is_dst(dt: datetime) -> bool:
    """Simple DST check: March-November = DST."""
    return 3 <= dt.month <= 10


def get_local_hour(lead: dict) -> int:
    """Get the current hour in the lead's local timezone."""
    state = _detect_state(lead)
    offset = STATE_TZ_OFFSETS.get(state, -5)
    
    # Apply DST (add 1 hour) except for AZ
    now_utc = datetime.now(timezone.utc)
    if state not in NO_DST_STATES and _is_dst(now_utc):
        offset += 1
    
    local_time = now_utc + timedelta(hours=offset)
    return local_time.hour


def is_contact_hours_for_lead(lead: dict) -> bool:
    """Check if it's 8 AM - 6 PM in the lead's local timezone.
    Used for SMS and calls only. Email is always allowed."""
    local_hour = get_local_hour(lead)
    # Also check day of week
    state = _detect_state(lead)
    offset = STATE_TZ_OFFSETS.get(state, -5)
    now_utc = datetime.now(timezone.utc)
    if state not in NO_DST_STATES and _is_dst(now_utc):
        offset += 1
    local_time = now_utc + timedelta(hours=offset)
    weekday = local_time.weekday()  # 0=Mon, 6=Sun
    
    if weekday == 6:  # Sunday — no SMS/calls
        return False
    
    return 8 <= local_hour < 18


# ============================================================
#  OPT-OUT DETECTION
# ============================================================
OPT_OUT_KEYWORDS = {
    "stop", "unsubscribe", "opt out", "optout", "remove me",
    "don't contact", "dont contact", "no more", "cancel",
    "take me off", "not interested", "leave me alone",
}

def is_opted_out(lead: dict, supabase) -> bool:
    """Check if lead has opted out via SMS reply or email."""
    contact_id = lead.get("ghl_contact_id", "")
    
    # Check outbound_touches for opt-out replies
    try:
        result = supabase.table("outbound_touches").select(
            "reply_text"
        ).eq("contact_id", contact_id).not_.is_("reply_text", "null").execute()
        
        for row in result.data:
            reply = (row.get("reply_text", "") or "").lower().strip()
            for keyword in OPT_OUT_KEYWORDS:
                if keyword in reply:
                    return True
    except:
        pass
    
    # Check if status is manually set to opted_out
    status = (lead.get("status", "") or "").lower()
    if status in ("opted_out", "unsubscribed", "do_not_contact"):
        return True
    
    return False


# ============================================================
#  NURTURE SEQUENCE DEFINITION
#  Day 0: Initial email (audit/value)
#  Day 1: Follow-up email (case study)
#  Day 3: SMS check-in
#  Day 5: Email (industry tip)
#  Day 7: Call attempt
#  Day 10: Email (special offer)
#  Day 14: SMS last chance
#  Day 21: Newsletter enrollment begins (weekly)
#  Then: Weekly newsletter forever until opt-out
# ============================================================
NURTURE_SEQUENCE = [
    {"day": 0, "channel": "email", "template": "initial_audit",
     "subject": "Quick question about {company}'s online visibility",
     "body": """Hi {first_name},

I was looking at businesses in {city} and noticed {company} might be missing out on some easy wins for online visibility.

We help local businesses like yours show up in AI search results (think ChatGPT, Google AI Overviews) — which is where more and more customers are looking.

Would you be open to a quick free audit? Takes 2 minutes and I'll send you the results.

Best,
Dan
AI Service Co
owner@aiserviceco.com"""},

    {"day": 1, "channel": "email", "template": "case_study",
     "subject": "How a {niche} in FL increased leads 40% with one change",
     "body": """Hi {first_name},

Quick follow-up — wanted to share something relevant.

We recently helped a {niche} improve their Google Business Profile and AI visibility. Within 30 days they saw a 40% increase in inbound leads.

The fix was surprisingly simple: making sure their business data was structured the way AI systems prefer to read it.

If you're curious, I can run the same analysis on {company} — completely free, no strings attached.

Just reply "yes" and I'll send it over.

Dan
AI Service Co"""},

    {"day": 3, "channel": "sms", "template": "sms_checkin",
     "body": "Hi {first_name}, Dan from AI Service Co. Sent you an email about {company}'s online visibility — did you get a chance to see it? Happy to do a free audit if you're interested. Reply STOP to opt out."},

    {"day": 5, "channel": "email", "template": "industry_tip",
     "subject": "3 things every {niche} should know about AI search",
     "body": """Hi {first_name},

Here are 3 quick things every {niche} owner should know about how AI is changing local search:

1. **AI Overviews now appear above Google results** — if your business isn't optimized for AI, you're invisible to a growing segment of searchers.

2. **Your Google Business Profile is your #1 asset** — AI systems pull directly from it. Missing hours, no photos, or incomplete categories = lost customers.

3. **Reviews matter more than ever** — AI systems weigh review sentiment heavily when deciding which businesses to recommend.

I put together a quick scorecard for {company} if you'd like to see where you stand. No cost, no obligation.

Dan
AI Service Co"""},

    {"day": 7, "channel": "call", "template": "call_attempt",
     "script": "Hi, this is Sarah calling from AI Service Co. I'm following up on an email we sent about {company}'s online visibility. We offer free AI search audits for local businesses. Is there a good time to chat?"},

    {"day": 10, "channel": "email", "template": "special_offer",
     "subject": "Free AI visibility report for {company}",
     "body": """Hi {first_name},

I wanted to follow up one more time — we've been helping {niche} businesses in {city} get found by AI search engines like ChatGPT and Google's AI Overviews.

I've already started a preliminary report for {company}. Want me to send it over?

All I need is a quick "yes" and I'll have it in your inbox within 24 hours.

Dan
AI Service Co
P.S. — This is genuinely free. We do this because when business owners see the data, they often want our help implementing the fixes."""},

    {"day": 14, "channel": "sms", "template": "sms_last_chance",
     "body": "Hi {first_name}, last follow-up from Dan at AI Service Co. We have a free AI visibility report ready for {company}. Want me to send it? Reply YES or STOP to opt out."},
]

# After day 21, leads enter the weekly newsletter
NEWSLETTER_START_DAY = 21


# ============================================================
#  WEEKLY NEWSLETTER CONTENT (Rotating Tips)
# ============================================================
NEWSLETTER_TEMPLATES = [
    {
        "subject": "📊 Weekly Business Boost: 3 Ways to Get More Google Reviews",
        "body": """Hi {first_name},

Here's your weekly business tip from AI Service Co:

**🌟 3 Ways to Get More Google Reviews This Week**

1. **Ask every happy customer** — Train your team to ask right after a great interaction: "Would you mind leaving us a quick Google review?"

2. **Make it easy** — Create a short link to your review page (search "Google review link generator") and put it on receipts, follow-up emails, and your website.

3. **Respond to EVERY review** — Google's algorithm rewards businesses that engage. Even a simple "Thank you!" boosts your visibility.

*Why it matters:* Businesses with 50+ reviews get 266% more leads from Google than those with fewer than 10.

— Dan, AI Service Co

Reply STOP to unsubscribe.""",
    },
    {
        "subject": "📱 Weekly Business Boost: Is Your Website Mobile-Ready?",
        "body": """Hi {first_name},

Weekly tip from AI Service Co:

**📱 Mobile-First: Why It Matters More Than Ever**

72% of local searches happen on phones. Here's a 2-minute check:
- Open your website on your phone right now
- Can you read everything without zooming?
- Does your phone number link to a tap-to-call?
- Does your address link to Google Maps?

If any answer is "no" — you're losing customers daily. Most website builders (Wix, Squarespace, WordPress) have mobile preview modes. Use them.

*Quick Win:* Just adding a tap-to-call button typically increases phone inquiries by 30%.

— Dan, AI Service Co

Reply STOP to unsubscribe.""",
    },
    {
        "subject": "🗺️ Weekly Business Boost: Optimize Your Google Business Profile",
        "body": """Hi {first_name},

This week's tip:

**🗺️ Your Google Business Profile: The Free Marketing Tool Most Businesses Ignore**

3 things to update today (takes 10 minutes):

1. **Add 5 new photos** — Businesses with photos get 42% more direction requests and 35% more website clicks.

2. **Update your business description** — Include your top 3 services and your city. Example: "Tampa's trusted {niche} since 2015. Specializing in [service 1], [service 2], and [service 3]."

3. **Post a Google Business update** — Just like social media, but on Google. Post a special offer or helpful tip once a week.

*Bonus:* Enable Google Messaging so customers can text you directly from Google search.

— Dan, AI Service Co

Reply STOP to unsubscribe.""",
    },
    {
        "subject": "⭐ Weekly Business Boost: Turn Negative Reviews Into Wins",
        "body": """Hi {first_name},

This week's tip from AI Service Co:

**⭐ How to Handle Negative Reviews (And Actually Benefit From Them)**

The playbook:
1. **Respond within 24 hours** — Speed shows you care.
2. **Acknowledge the issue** — "We're sorry you had this experience."
3. **Take it offline** — "Please call us at [number] so we can make this right."
4. **Follow up** — After resolving, kindly ask if they'd update their review.

*The truth:* Businesses with a mix of reviews (4.2-4.5 stars) actually convert BETTER than perfect 5.0 ratings. People trust authenticity.

*One more thing:* Never pay for fake reviews. Google is removing them aggressively and penalizing businesses that use them.

— Dan, AI Service Co

Reply STOP to unsubscribe.""",
    },
]


# ============================================================
#  NURTURE DISPATCH ENGINE
# ============================================================

def _fill_template(template: str, lead: dict) -> str:
    """Replace {placeholders} in template with lead data."""
    try:
        rr = json.loads(lead.get("raw_research", "{}") or "{}")
    except:
        rr = {}
    
    full_name = (lead.get("full_name", "") or "").strip()
    first_name = full_name.split()[0] if full_name else "there"
    
    replacements = {
        "first_name": first_name if first_name and first_name != "Business" else "there",
        "company": lead.get("company_name", "your business") or "your business",
        "city": rr.get("search_query", "").split()[-1] if rr.get("search_query") else "your area",
        "niche": lead.get("niche", "business") or "business",
    }
    
    result = template
    for key, val in replacements.items():
        result = result.replace("{" + key + "}", str(val))
    return result


def _send_nurture_email(lead: dict, subject: str, body: str, supabase) -> bool:
    """Send a nurture email via Resend and log to outbound_touches."""
    email = (lead.get("email", "") or "").strip()
    if not email:
        return False
    
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("  ❌ No RESEND_API_KEY")
        return False
    
    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
    
    try:
        r = requests.post("https://api.resend.com/emails", headers={
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
        }, json={
            "from": from_email,
            "to": [email],
            "subject": subject,
            "text": body,
        }, timeout=15)
        
        success = r.status_code in [200, 201]
        resend_id = ""
        if success:
            try:
                resend_id = r.json().get("id", "")
            except:
                pass
        
        # Log to outbound_touches
        supabase.table("outbound_touches").insert({
            "contact_id": lead.get("ghl_contact_id", ""),
            "channel": "email",
            "status": "sent" if success else "failed",
            "subject": subject[:200],
            "body_preview": body[:300],
            "resend_email_id": resend_id,
            "metadata": json.dumps({"type": "nurture", "template": "drip"}),
        }).execute()
        
        return success
    except Exception as e:
        print(f"  ❌ Nurture email error: {e}")
        return False


def _send_nurture_sms(lead: dict, body: str, supabase) -> bool:
    """Send an SMS via GHL webhook and log."""
    phone = (lead.get("phone", "") or "").strip()
    if not phone:
        return False
    
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not webhook_url:
        print("  ❌ No GHL_SMS_WEBHOOK_URL")
        return False
    
    try:
        r = requests.post(webhook_url, json={
            "phone": phone,
            "message": body,
            "contact_name": lead.get("full_name", ""),
            "company_name": lead.get("company_name", ""),
        }, timeout=15)
        
        success = r.status_code in [200, 201]
        
        supabase.table("outbound_touches").insert({
            "contact_id": lead.get("ghl_contact_id", ""),
            "channel": "sms",
            "status": "sent" if success else "failed",
            "body_preview": body[:300],
            "metadata": json.dumps({"type": "nurture", "template": "drip"}),
        }).execute()
        
        return success
    except Exception as e:
        print(f"  ❌ Nurture SMS error: {e}")
        return False


def _make_nurture_call(lead: dict, supabase) -> bool:
    """Place a call via Vapi and log."""
    phone = (lead.get("phone", "") or "").strip()
    if not phone:
        return False
    
    vapi_key = os.environ.get("VAPI_PRIVATE_KEY")
    phone_id = os.environ.get("VAPI_PHONE_NUMBER_ID", "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e")
    assistant_id = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah 3.0
    
    if not vapi_key:
        print("  ❌ No VAPI_PRIVATE_KEY")
        return False
    
    # Clean phone number
    import re
    digits = re.sub(r'[^\d+]', '', phone)
    if not digits.startswith("+"):
        if len(digits) == 11 and digits.startswith("1"):
            phone = "+" + digits
        else:
            phone = "+1" + digits
    else:
        phone = digits
    
    try:
        r = requests.post("https://api.vapi.ai/call", headers={
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json",
        }, json={
            "type": "outboundPhoneCall",
            "phoneNumberId": phone_id,
            "assistantId": assistant_id,
            "customer": {
                "number": phone,
                "name": lead.get("company_name", "Prospect"),
            },
            "metadata": {
                "company_name": lead.get("company_name", ""),
                "source": "nurture_drip",
            }
        }, timeout=15)
        
        success = r.status_code in [200, 201]
        call_id = ""
        if success:
            try:
                call_id = r.json().get("id", "")
            except:
                pass
        
        supabase.table("outbound_touches").insert({
            "contact_id": lead.get("ghl_contact_id", ""),
            "channel": "call",
            "status": "sent" if success else "failed",
            "body_preview": f"Nurture call to {phone}",
            "metadata": json.dumps({"type": "nurture", "call_id": call_id}),
        }).execute()
        
        return success
    except Exception as e:
        print(f"  ❌ Nurture call error: {e}")
        return False


# ============================================================
#  MAIN NURTURE PROCESSOR
# ============================================================

def run_nurture_cycle(max_actions: int = 20):
    """
    Process the nurture queue. Called by system_orchestrator.
    
    For each lead in 'contacted' or 'nurture' status:
    1. Check opt-out
    2. Determine which drip step they're on (based on days since first touch)
    3. Execute the appropriate action (email/SMS/call)
    4. Respect timezone for SMS/calls
    
    For leads past day 21: send weekly newsletter
    """
    from modules.database.supabase_client import get_supabase
    
    supabase = get_supabase()
    
    print(f"\n{'='*50}")
    print(f"📬 NURTURE ENGINE v1.0 — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*50}")
    
    # Pull leads that need nurturing
    # Status: 'contacted' (had first outreach) or 'nurture' (explicitly in nurture)
    result = supabase.table("contacts_master").select(
        "ghl_contact_id,full_name,email,phone,company_name,niche,status,lead_source,raw_research,created_at"
    ).in_("status", ["contacted", "nurture"]).limit(200).execute()
    
    leads = result.data or []
    print(f"📊 Found {len(leads)} leads in nurture pipeline")
    
    actions_taken = 0
    emails_sent = 0
    sms_sent = 0
    calls_made = 0
    skipped_optout = 0
    skipped_hours = 0
    skipped_recent = 0
    
    for lead in leads:
        if actions_taken >= max_actions:
            break
        
        contact_id = lead.get("ghl_contact_id", "")
        company = lead.get("company_name", "Unknown")
        
        # 1. Check opt-out
        if is_opted_out(lead, supabase):
            skipped_optout += 1
            continue
        
        # 2. Get last touch for this lead
        touches = supabase.table("outbound_touches").select(
            "ts,channel,metadata"
        ).eq("contact_id", contact_id).order("ts", desc=True).limit(5).execute()
        
        touch_data = touches.data or []
        
        # Calculate days since first touch
        if touch_data:
            first_touch = touch_data[-1]  # Oldest
            try:
                first_ts = datetime.fromisoformat(first_touch["ts"].replace("Z", "+00:00"))
                days_since_first = (datetime.now(timezone.utc) - first_ts).days
            except:
                days_since_first = 0
            
            # Check last touch — don't spam (min 20 hours between touches)
            try:
                last_ts = datetime.fromisoformat(touch_data[0]["ts"].replace("Z", "+00:00"))
                hours_since_last = (datetime.now(timezone.utc) - last_ts).total_seconds() / 3600
            except:
                hours_since_last = 999
            
            if hours_since_last < 20:
                skipped_recent += 1
                continue
        else:
            days_since_first = 0
            hours_since_last = 999
        
        # 3. Determine which nurture step
        # Find the right step from the sequence
        step = None
        for s in reversed(NURTURE_SEQUENCE):
            if days_since_first >= s["day"]:
                step = s
                break
        
        # Check if this specific template was already sent
        if step:
            template_name = step.get("template", "")
            already_sent = False
            for t in touch_data:
                try:
                    meta = json.loads(t.get("metadata", "{}") or "{}")
                    if meta.get("template") == template_name:
                        already_sent = True
                        break
                except:
                    pass
            
            if already_sent:
                # Check if past newsletter start
                if days_since_first >= NEWSLETTER_START_DAY:
                    step = None  # Fall through to newsletter
                else:
                    continue  # Already sent this step, wait for next day
        
        # 4. Execute the action
        if step:
            channel = step["channel"]
            print(f"\n  📌 {company} | Day {days_since_first} | {channel} ({step['template']})")
            
            if channel == "email":
                subject = _fill_template(step["subject"], lead)
                body = _fill_template(step["body"], lead)
                if _send_nurture_email(lead, subject, body, supabase):
                    emails_sent += 1
                    actions_taken += 1
                    # Log template name
                    supabase.table("outbound_touches").update({
                        "metadata": json.dumps({"type": "nurture", "template": step["template"]})
                    }).eq("contact_id", contact_id).order("ts", desc=True).limit(1).execute()
                    
            elif channel == "sms":
                if not is_contact_hours_for_lead(lead):
                    skipped_hours += 1
                    print(f"    ⏰ Outside hours for lead's timezone")
                    continue
                body = _fill_template(step["body"], lead)
                if _send_nurture_sms(lead, body, supabase):
                    sms_sent += 1
                    actions_taken += 1
                    
            elif channel == "call":
                if not is_contact_hours_for_lead(lead):
                    skipped_hours += 1
                    print(f"    ⏰ Outside hours for lead's timezone")
                    continue
                if _make_nurture_call(lead, supabase):
                    calls_made += 1
                    actions_taken += 1
        
        # 5. Weekly newsletter (for leads past day 21)
        elif days_since_first >= NEWSLETTER_START_DAY:
            # Check if we sent a newsletter in the last 6 days
            newsletter_recent = False
            for t in touch_data:
                try:
                    meta = json.loads(t.get("metadata", "{}") or "{}")
                    if meta.get("type") == "newsletter":
                        t_ts = datetime.fromisoformat(t["ts"].replace("Z", "+00:00"))
                        if (datetime.now(timezone.utc) - t_ts).days < 6:
                            newsletter_recent = True
                            break
                except:
                    pass
            
            if newsletter_recent:
                continue
            
            # Pick newsletter template based on week number
            week_num = (days_since_first - NEWSLETTER_START_DAY) // 7
            template = NEWSLETTER_TEMPLATES[week_num % len(NEWSLETTER_TEMPLATES)]
            
            subject = _fill_template(template["subject"], lead)
            body = _fill_template(template["body"], lead)
            
            print(f"\n  📰 {company} | Day {days_since_first} | Newsletter #{week_num + 1}")
            
            if _send_nurture_email(lead, subject, body, supabase):
                emails_sent += 1
                actions_taken += 1
                # Update metadata to mark as newsletter
                supabase.table("outbound_touches").update({
                    "metadata": json.dumps({"type": "newsletter", "week": week_num + 1})
                }).eq("contact_id", contact_id).order("ts", desc=True).limit(1).execute()
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📬 NURTURE SUMMARY")
    print(f"  📧 Emails sent: {emails_sent}")
    print(f"  📱 SMS sent: {sms_sent}")
    print(f"  📞 Calls made: {calls_made}")
    print(f"  🚫 Skipped (opt-out): {skipped_optout}")
    print(f"  ⏰ Skipped (outside hours): {skipped_hours}")
    print(f"  ⏳ Skipped (too recent): {skipped_recent}")
    print(f"{'='*50}")
    
    return {
        "emails": emails_sent,
        "sms": sms_sent,
        "calls": calls_made,
        "skipped_optout": skipped_optout,
        "skipped_hours": skipped_hours,
        "total_actions": actions_taken,
    }
