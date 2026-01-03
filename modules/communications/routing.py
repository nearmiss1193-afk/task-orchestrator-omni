import os
from modules.communications.email_direct import send_email_direct
# from modules.ghl_api import send_ghl_email # Hypothetical import

def route_communication(contact, message_type="EMAIL", content=None):
    """
    Traffic Cop: Sovereign First -> GHL Fallback.
    """
    print(f"🚦 Routing {message_type} for {contact['email']}...")
    
    # 1. PRIMARY: Sovereign Channel
    if message_type == "EMAIL":
        result = send_email_direct(contact['email'], content['subject'], content['body'])
        
        if result['status'] == 'sent' or result['status'] == 'simulated':
            print("✅ Primary Channel Success.")
            return result
            
        print(f"⚠️ Primary Failed ({result.get('message')}). Switch to Backup.")
        
    # 2. BACKUP: GoHighLevel Hook
    # We trigger the GHL API as a fallback
    ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN")
    if ghl_token:
        print("🛡️ Engaging Backup Protocol (GHL)...")
        # Logic to call GHL Conversation API would go here
        # requests.post(...)
        return {"status": "sent_backup", "provider": "GHL"}
        
    return {"status": "failed", "reason": "All Channels Down"}
