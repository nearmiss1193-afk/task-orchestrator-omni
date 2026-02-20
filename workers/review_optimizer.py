"""
SMART REVIEW OPTIMIZER v1.0
===========================
Post-service follow-up that gates reviews intelligently:
- 4-5 stars → Google review link
- 1-3 stars → Internal alert for manager callback

Called by: SMS inbound webhook (rating replies) or manually via API
"""
import os
import json
import requests
from datetime import datetime, timezone


# ============================================================
#  CONFIGURATION
# ============================================================

# Google review link template — client replaces with their actual Place ID
# Format: https://search.google.com/local/writereview?placeid=PLACE_ID
DEFAULT_REVIEW_URL = "https://search.google.com/local/reviews?placeid={place_id}"

# Dan's alert phone for internal issues
MANAGER_ALERT_PHONE = os.environ.get("MANAGER_PHONE", "")
MANAGER_ALERT_EMAIL = os.environ.get("MANAGER_EMAIL", "owner@aiserviceco.com")


# ============================================================
#  REVIEW REQUEST — Send post-service SMS
# ============================================================

def send_review_request(contact_id: str, customer_name: str, customer_phone: str,
                        company_name: str, supabase) -> dict:
    """
    Send a post-service SMS asking the customer to rate their experience 1-5.
    
    Args:
        contact_id: GHL contact ID or internal ID
        customer_name: Customer's first name
        customer_phone: Customer's phone number
        company_name: The business that provided the service
        supabase: Supabase client
    
    Returns:
        dict with status and details
    """
    first_name = customer_name.split()[0] if customer_name else "there"
    
    message = (
        f"Hi {first_name}! Thanks for choosing {company_name}. "
        f"We'd love your feedback — how was your experience? "
        f"Reply with a number 1-5 (5 = amazing). "
        f"Reply STOP to opt out."
    )
    
    # Send via GHL SMS webhook
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not webhook_url:
        print("  ❌ No GHL_SMS_WEBHOOK_URL")
        return {"status": "failed", "error": "no_webhook"}
    
    try:
        r = requests.post(webhook_url, json={
            "phone": customer_phone,
            "message": message,
            "contact_name": customer_name,
            "company_name": company_name,
        }, timeout=15)
        
        success = r.status_code in [200, 201]
        
        # Log to outbound_touches
        supabase.table("outbound_touches").insert({
            "contact_id": contact_id,
            "channel": "sms",
            "status": "sent" if success else "failed",
            "body_preview": message[:300],
            "metadata": json.dumps({
                "type": "review_request",
                "company_name": company_name,
                "awaiting_rating": True,
            }),
        }).execute()
        
        # Track in system_state for pending ratings
        supabase.table("system_state").upsert({
            "key": f"review_pending_{customer_phone}",
            "status": "awaiting_rating",
            "last_error": json.dumps({
                "contact_id": contact_id,
                "company_name": company_name,
                "customer_name": customer_name,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            }),
        }, on_conflict="key").execute()
        
        print(f"  ⭐ Review request sent to {customer_name} ({customer_phone})")
        return {"status": "sent", "phone": customer_phone}
        
    except Exception as e:
        print(f"  ❌ Review request error: {e}")
        return {"status": "failed", "error": str(e)}


# ============================================================
#  HANDLE RATING — Route based on score
# ============================================================

def handle_rating(customer_phone: str, rating: int, supabase,
                  google_place_id: str = None) -> dict:
    """
    Process a customer's rating response.
    
    - 4-5: Send Google review link
    - 1-3: Alert manager for internal resolution (never hits Google)
    
    Args:
        customer_phone: Phone that sent the rating
        rating: Integer 1-5
        supabase: Supabase client
        google_place_id: Optional Google Place ID for review link
    
    Returns:
        dict with action taken
    """
    # Look up the pending review request
    pending = supabase.table("system_state").select("*").eq(
        "key", f"review_pending_{customer_phone}"
    ).execute()
    
    if not pending.data:
        print(f"  ⚠️ No pending review for {customer_phone}")
        return {"status": "no_pending", "phone": customer_phone}
    
    context = {}
    try:
        context = json.loads(pending.data[0].get("last_error", "{}"))
    except:
        pass
    
    contact_id = context.get("contact_id", "")
    company_name = context.get("company_name", "our team")
    customer_name = context.get("customer_name", "Customer")
    first_name = customer_name.split()[0] if customer_name else "there"
    
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    result = {"rating": rating, "phone": customer_phone, "company": company_name}
    
    if rating >= 4:
        # ===== POSITIVE: Send Google review link =====
        if google_place_id:
            review_url = DEFAULT_REVIEW_URL.format(place_id=google_place_id)
        else:
            # Fallback: generic search
            safe_name = company_name.replace(" ", "+")
            review_url = f"https://www.google.com/search?q={safe_name}+reviews"
        
        message = (
            f"Thank you {first_name}! We're so glad you had a great experience. 🌟\n\n"
            f"Would you mind sharing that on Google? It really helps us grow:\n"
            f"{review_url}\n\n"
            f"Thank you! — {company_name}"
        )
        
        if webhook_url:
            try:
                requests.post(webhook_url, json={
                    "phone": customer_phone,
                    "message": message,
                }, timeout=15)
            except:
                pass
        
        # Log positive result
        supabase.table("outbound_touches").insert({
            "contact_id": contact_id,
            "channel": "sms",
            "status": "sent",
            "body_preview": message[:300],
            "metadata": json.dumps({
                "type": "review_positive",
                "rating": rating,
                "review_url": review_url,
            }),
        }).execute()
        
        result["action"] = "google_review_link_sent"
        result["review_url"] = review_url
        print(f"  ⭐ {rating}/5 from {first_name} → Google review link sent")
    
    else:
        # ===== NEGATIVE: Internal alert, never Google =====
        message = (
            f"Thank you for your feedback {first_name}. We're sorry your experience "
            f"wasn't what you expected. A manager will reach out within the hour to "
            f"make things right. — {company_name}"
        )
        
        if webhook_url:
            try:
                requests.post(webhook_url, json={
                    "phone": customer_phone,
                    "message": message,
                }, timeout=15)
            except:
                pass
        
        # Alert the manager
        _alert_manager(
            customer_name=customer_name,
            customer_phone=customer_phone,
            company_name=company_name,
            rating=rating,
            supabase=supabase,
        )
        
        # Log negative result
        supabase.table("outbound_touches").insert({
            "contact_id": contact_id,
            "channel": "sms",
            "status": "sent",
            "body_preview": message[:300],
            "metadata": json.dumps({
                "type": "review_negative",
                "rating": rating,
                "action": "manager_alert",
            }),
        }).execute()
        
        result["action"] = "manager_alerted"
        print(f"  ⚠️ {rating}/5 from {first_name} → Manager alerted, Google blocked")
    
    # Clear the pending state
    supabase.table("system_state").update({
        "status": f"rated_{rating}",
    }).eq("key", f"review_pending_{customer_phone}").execute()
    
    return result


# ============================================================
#  MANAGER ALERT (Internal)
# ============================================================

def _alert_manager(customer_name: str, customer_phone: str,
                   company_name: str, rating: int, supabase):
    """Send internal alert to manager about unhappy customer."""
    
    # SMS alert to manager
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    manager_phone = MANAGER_ALERT_PHONE
    
    if webhook_url and manager_phone:
        alert_msg = (
            f"🚨 REVIEW ALERT: {customer_name} rated {rating}/5 for {company_name}. "
            f"Call them ASAP: {customer_phone}. "
            f"Fix before they go to Google!"
        )
        try:
            requests.post(webhook_url, json={
                "phone": manager_phone,
                "message": alert_msg,
            }, timeout=15)
            print(f"  📱 Manager SMS alert sent")
        except:
            pass
    
    # Email alert to manager
    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key:
        try:
            requests.post("https://api.resend.com/emails", headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json",
            }, json={
                "from": "AI Service Co <owner@aiserviceco.com>",
                "to": [MANAGER_ALERT_EMAIL],
                "subject": f"🚨 Unhappy Customer: {customer_name} ({rating}/5)",
                "text": (
                    f"URGENT: Customer needs callback\n\n"
                    f"Customer: {customer_name}\n"
                    f"Phone: {customer_phone}\n"
                    f"Rating: {rating}/5\n"
                    f"Business: {company_name}\n\n"
                    f"They've been told a manager will call within the hour.\n"
                    f"Their feedback has NOT been sent to Google.\n\n"
                    f"— AI Service Co Review Optimizer"
                ),
            }, timeout=15)
            print(f"  📧 Manager email alert sent")
        except:
            pass


# ============================================================
#  REVIEW STATS (for Dashboard)
# ============================================================

def get_review_stats(supabase) -> dict:
    """Get review optimizer funnel metrics."""
    from datetime import timedelta
    
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    
    # Count review requests sent
    requests_sent = supabase.table("outbound_touches").select(
        "id", count="exact"
    ).eq("channel", "sms").filter(
        "metadata", "cs", '{"type": "review_request"}'
    ).gte("ts", week_ago).execute()
    
    # Count positive (Google links sent)
    positive = supabase.table("outbound_touches").select(
        "id", count="exact"
    ).filter(
        "metadata", "cs", '{"type": "review_positive"}'
    ).gte("ts", week_ago).execute()
    
    # Count negative (manager alerts)
    negative = supabase.table("outbound_touches").select(
        "id", count="exact"
    ).filter(
        "metadata", "cs", '{"type": "review_negative"}'
    ).gte("ts", week_ago).execute()
    
    sent = requests_sent.count or 0
    pos = positive.count or 0
    neg = negative.count or 0
    
    return {
        "period": "7d",
        "requests_sent": sent,
        "positive_ratings": pos,
        "negative_ratings": neg,
        "google_links_sent": pos,
        "issues_caught": neg,
        "response_rate": f"{((pos + neg) / sent * 100):.0f}%" if sent > 0 else "0%",
    }
