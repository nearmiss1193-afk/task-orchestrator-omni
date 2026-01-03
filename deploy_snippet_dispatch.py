
def dispatch_email_logic(lead):
    """
    SHARED LOGIC: Sends the Day 0 Email via GHL.
    Used by: 
    1. outreach_scaling_loop (Batch)
    2. research_lead_logic (Turbo - Instant)
    """
    import requests
    import os
    
    contact_id = lead['ghl_contact_id']
    research = lead.get('raw_research', {}) or {}
    segment = research.get('campaign_segment', 'A') 
    
    ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN") 
    ghl_location_id = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        'Authorization': f'Bearer {ghl_token}', 
        'Version': '2021-07-28', 
        'Content-Type': 'application/json',
        'Location-Id': ghl_location_id
    }
    
    subject = f"question re: {lead.get('full_name', 'your site')}"
    body = f"hey {lead.get('full_name', 'there').split()[0].lower()},\n\n{research.get('hook', 'saw your site and noticed a quick fix for your lead form.')}\n\nmind if i send over a 30s video showing exactly how to fix it?"
    
    payload = {"type": "Email", "contactId": contact_id, "subject": subject, "body": body}
    
    try:
        # Check if already nurtured to avoid double-send (Safety)
        if lead.get('status') == 'nurtured':
            brain_log(f"Skipping {contact_id}: Already Nurtured.")
            return False

        res = requests.post("https://services.leadconnectorhq.com/conversations/messages", json=payload, headers=headers)
        
        if res.status_code in [200, 201]:
            brain_log(f"🚀 Cloud Outreach Sent to {contact_id}")
            return True
        else:
            brain_log(f"❌ GHL Dispatch Error {res.status_code}: {res.text}")
            return False
            
    except Exception as e:
        brain_log(f"❌ Dispatch Exception: {str(e)}")
        return False
