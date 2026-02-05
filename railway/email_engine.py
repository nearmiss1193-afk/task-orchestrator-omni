"""
Email Engine - Triggers outreach for enriched leads
Runs every 30 minutes via Railway Cron
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import shared clients
from supabase_client import (
    get_client, 
    get_outreachable_leads, 
    update_lead_status,
    log_outbound_touch,
    check_recent_touch
)
from ghl_client import create_contact, trigger_outreach_workflow, send_email

# Email templates based on traffic light
EMAIL_TEMPLATES = {
    "RED": {
        "subject": "🔴 {business_name} - Your website is costing you customers",
        "body": """Hi there,

I just ran an automated audit on {business_name}'s online presence and found some urgent issues:

🔴 **Critical Problems Found:**
{issues}

These issues are actively costing you leads and customers right now.

I've prepared a free, detailed audit report showing exactly what's wrong and how to fix it.

**Would you like me to send it over?**

Just reply "Yes" and I'll send it immediately.

Best,
AI Service Co
"""
    },
    "YELLOW": {
        "subject": "🟡 {business_name} - Quick website improvements that could double your leads",
        "body": """Hi there,

I ran an audit on {business_name}'s website and found some areas for improvement:

🟡 **Areas Needing Attention:**
{issues}

These aren't critical, but fixing them could significantly increase your lead flow.

I've prepared a free audit report with specific recommendations.

**Want me to send it to you?**

Just reply "Yes" to get it.

Best,
AI Service Co
"""
    }
}


def format_issues(lead: dict) -> str:
    """Format issues based on lead data"""
    issues = []
    
    if not lead.get("website_url"):
        issues.append("• No website found - you're invisible to online searchers")
    
    if lead.get("pagespeed_score") and lead["pagespeed_score"] < 50:
        issues.append(f"• Website speed score: {lead['pagespeed_score']}/100 (Google penalizes slow sites)")
    
    if not lead.get("ssl_status"):
        issues.append("• Missing SSL certificate - browsers show 'Not Secure' warning")
    
    if not lead.get("forms_present"):
        issues.append("• No contact forms found - you're losing leads who want to reach you")
    
    if not lead.get("legal_compliance"):
        issues.append("• Missing privacy policy - potential legal liability")
    
    if lead.get("pagespeed_seo") and lead["pagespeed_seo"] < 70:
        issues.append(f"• SEO score: {lead['pagespeed_seo']}/100 - you're not ranking well on Google")
    
    return "\n".join(issues) if issues else "• Multiple areas need attention"


def should_send_outreach(lead: dict) -> bool:
    """Determine if we should send outreach to this lead"""
    # Skip GREEN leads - low priority
    if lead.get("traffic_light") == "GREEN":
        return False
    
    # Check if already contacted recently
    if check_recent_touch(lead["id"], days=7):
        return False
    
    # Must have email or will create in GHL
    if not lead.get("email") and not lead.get("phone"):
        return False
    
    return True


def send_outreach(lead: dict) -> dict:
    """Send outreach email for a single lead"""
    traffic_light = lead.get("traffic_light", "YELLOW")
    template = EMAIL_TEMPLATES.get(traffic_light, EMAIL_TEMPLATES["YELLOW"])
    
    # Format email
    issues = format_issues(lead)
    subject = template["subject"].format(business_name=lead.get("business_name", "Your Business"))
    body = template["body"].format(
        business_name=lead.get("business_name", "Your Business"),
        issues=issues
    )
    
    try:
        # Create or get contact in GHL
        ghl_contact = create_contact({
            "first_name": lead.get("contact_name", "").split()[0] if lead.get("contact_name") else "",
            "last_name": " ".join(lead.get("contact_name", "").split()[1:]) if lead.get("contact_name") else "",
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "company_name": lead.get("business_name"),
            "website_url": lead.get("website_url")
        })
        
        ghl_contact_id = ghl_contact.get("contact", {}).get("id")
        
        if ghl_contact_id:
            # Trigger the outreach workflow
            trigger_outreach_workflow(ghl_contact_id)
            
            # Log the touch
            log_outbound_touch(
                contact_id=lead["id"],
                touch_type="email_initial",
                touch_status="sent",
                report_data={
                    "ghl_contact_id": ghl_contact_id,
                    "traffic_light": traffic_light,
                    "subject": subject
                }
            )
            
            return {"success": True, "ghl_contact_id": ghl_contact_id}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Unknown error"}


def run_outreach_cycle():
    """Main outreach cycle - run this every 30 minutes"""
    print(f"\n{'='*60}")
    print(f"📧 EMAIL ENGINE - {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Get enriched leads ready for outreach
    leads = get_outreachable_leads(limit=20)  # Process 20 at a time
    print(f"📋 Found {len(leads)} leads ready for outreach\n")
    
    sent_count = 0
    skipped_count = 0
    error_count = 0
    
    for lead in leads:
        print(f"\n🏢 {lead.get('business_name', 'Unknown')}")
        light = lead.get("traffic_light", "?")
        
        if not should_send_outreach(lead):
            print(f"   ⏭️ Skipped (recently contacted or low priority)")
            skipped_count += 1
            continue
        
        result = send_outreach(lead)
        
        if result.get("success"):
            print(f"   ✅ {'🔴' if light == 'RED' else '🟡'} Email triggered via GHL")
            update_lead_status(lead["id"], "outreached")
            sent_count += 1
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
            error_count += 1
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"📈 OUTREACH RESULTS:")
    print(f"   ✅ Sent:    {sent_count}")
    print(f"   ⏭️ Skipped: {skipped_count}")
    print(f"   ❌ Errors:  {error_count}")
    print(f"{'='*60}\n")
    
    return {
        "sent": sent_count,
        "skipped": skipped_count,
        "errors": error_count
    }


if __name__ == "__main__":
    run_outreach_cycle()
