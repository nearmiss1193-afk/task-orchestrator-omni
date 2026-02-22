import os
import json
import traceback
from datetime import datetime

def parse_contact_status(contact_id: str):
    from modules.database.supabase_client import get_supabase
    
    supabase = get_supabase()
    result = supabase.table("contacts_master").select("company_name, website_url, phone, full_name, onboarding_status").eq("ghl_contact_id", contact_id).execute()
    
    if len(result.data) == 0:
        return {"status": "error", "message": f"Contact {contact_id} not found."}
    
    contact = result.data[0]
    onboarding_status = contact.get("onboarding_status") or {}
    
    if onboarding_status.get("is_fulfilled"):
        return {"status": "ignored", "message": "Zero-Touch already fulfilled."}
        
    company_name = contact.get('company_name') or 'N/A'
    website_url = contact.get('website_url') or 'N/A'
    full_name = contact.get('full_name') or 'Team'
    phone = contact.get('phone') or ''
    first_name = full_name.split(' ')[0] if full_name else 'there'
    
    # We need the actual contact record for some updates
    res_full = supabase.table("contacts_master").select("*").eq("ghl_contact_id", contact_id).execute()
    if not res_full.data:
        return {"status": "error", "message": "Could not retrieve full contact data"}
    lead = res_full.data[0]
    lead_id = lead.get("id")
    lead_email = lead.get("email")

    print(f"🚀 Firing Zero-Touch Fulfillment for {company_name} ({website_url})")
    fulfillment_details = {}
    
    # 1. Scraping & Research Enrichment
    print(f"  [1/4] Starting Web Profiling for {website_url}...")
    from workers.audit_generator import fetch_pagespeed, check_privacy_policy, check_ai_readiness
    from datetime import timezone
    
    ps_data = fetch_pagespeed(website_url) if website_url != 'N/A' else {}
    privacy_data = check_privacy_policy(website_url) if website_url != 'N/A' else {}
    ai_data = check_ai_readiness(website_url) if website_url != 'N/A' else {}
    
    raw_research = json.loads(lead.get("raw_research") or "{}")
    raw_research.update({
        "pagespeed": ps_data,
        "privacy": privacy_data,
        "ai_readiness": ai_data,
        "audited_at": datetime.now(timezone.utc).isoformat()
    })
    
    supabase.table("contacts_master").update({"raw_research": json.dumps(raw_research)}).eq("id", lead_id).execute()
    fulfillment_details["research_enriched"] = True
    
    # 2. 14 Days of Social Posts Generation
    print("  [2/4] Generating 14-Day Social Campaign...")
    # NOTE: Deep generation runs via auto_social_content_cycle cron. We just mark it queued.
    fulfillment_details["social_campaign_queued"] = True
    
    sample_social_post = f"Excited to highlight {company_name}! They are setting new standards in their industry. We can't wait to see what they achieve next. #Innovation #Growth #B2B"
    try:
        import google.generativeai as genai
        # If genai is installed, make a punchy sample
        if os.environ.get("GEMINI_API_KEY"):
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            prompt = f"Write a professional, engaging 2-sentence LinkedIn post introducing {company_name} and the value they bring to their clients. Make it punchy, B2B focused, and include relevant hashtags."
            response = model.generate_content(prompt)
            if response and response.text:
                sample_social_post = response.text.replace('"', '').replace("'", "")
    except Exception as e:
        print(f"   ⚠️ Gemini generation error, using fallback: {e}")

    # 3. SEO Audit Generation
    print("  [3/4] Packaging SEO/Privacy Audit Report...")
    audit_link = f"https://aiserviceco.com/audit?id={lead_id}"
    score = ps_data.get("score") if isinstance(ps_data, dict) else "N/A"
    fulfillment_details["audit_score"] = score
    
    # 4. Email Delivery via Resend
    print("  [4/4] Dispatching Welcome Asset Email via Resend...")
    if lead_email:
        try:
            import requests
            resend_key = os.environ.get("RESEND_API_KEY")
            from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
            
            email_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                <h2>Welcome aboard, {first_name}! 🚀</h2>
                <p>Your payment was successful, and our systems have already begun working on your <strong>{company_name}</strong> account.</p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #020617;">1. Your AI Readiness & Performance Audit</h3>
                    <p>We ran a deep scan on <strong>{website_url}</strong>. Your initial technical score is <strong>{score}/100</strong>.</p>
                    <p>You can view your full technical breakdown on your interactive dashboard.</p>
                    <a href="{audit_link}" style="display:inline-block; background:#2563eb; color:#fff; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold;">View Your Dashboard</a>
                </div>

                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #020617;">2. Content Engine Activation</h3>
                    <p>Your social media generation engine has been queued. Our agents are analyzing your brand and building your first 14 days of content. Here's a sample of what we're crafting for you right now:</p>
                    <blockquote style="font-style: italic; border-left: 4px solid #cbd5e1; padding-left: 10px; color: #475569;">
                        {sample_social_post}
                    </blockquote>
                </div>
                
                <p>Our team will reach out shortly to finalize your onboarding and connect your social accounts via Ayrshare.</p>
                <p>Talk soon,<br><strong>Sovereign Operations</strong></p>
            </div>
            """
            
            r = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={
                    "from": from_email,
                    "to": [lead_email],
                    "subject": f"🚀 Initial Setup & Audit Assets for {company_name}",
                    "html": email_html,
                },
                timeout=15
            )
            if r.status_code in [200, 201]:
                print(f"  ✅ Welcome Email Successfully Sent to {lead_email}")
                fulfillment_details["email_sent"] = True
            else:
                print(f"  ⚠️ Email delivery issue: {r.status_code} - {r.text}")
                fulfillment_details["email_sent"] = False
                fulfillment_details["email_error"] = r.text
        except Exception as e:
            print(f"  ❌ Fatal email dispatch error: {e}")
            fulfillment_details["email_sent"] = False
    else:
        print("  ⚠️ No email found for lead, skipping welcome email.")
        fulfillment_details["email_sent"] = False
        fulfillment_details["email_error"] = "no_email_address"
        
    # Mark fulfilled
    onboarding_status["is_fulfilled"] = True
    onboarding_status["fulfilled_at"] = datetime.now(timezone.utc).isoformat()
    onboarding_status["details"] = fulfillment_details
    
    supabase.table("contacts_master").update({"onboarding_status": onboarding_status}).eq("ghl_contact_id", contact_id).execute()
    
    print(f"✅ Zero-Touch Sequence Complete for {company_name}!")
    return {"status": "success", "message": f"Successfully zero-touch fulfilled {company_name}"}

def trigger_zero_touch(contact_id: str):
    """
    Called asynchronously by Modal
    """
    try:
        res = parse_contact_status(contact_id)
        print(f"Zero-Touch Result: {res}")
        return res
    except Exception as e:
        print(f"❌ Failed to run zero-touch sequence: {e}")
        # Could route back to autonomous_inspector here
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Internal testing
    trigger_zero_touch("test_lead_123")
