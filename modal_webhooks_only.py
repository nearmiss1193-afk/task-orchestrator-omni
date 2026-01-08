"""
MODAL WEBHOOKS ONLY (FAST DEPLOY)
=================================
Deploys just the critical webhooks without the heavy worker.
"""
import modal
import os

app = modal.App("empire-webhooks-live")

image = modal.Image.debian_slim().pip_install(
    "requests",
    "python-dotenv",
    "supabase",
    "fastapi"
)

# ============ VAPI CALLBACK (Critical for Phone) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    keep_warm=1
)
@modal.web_endpoint(method="POST", label="vapi-live")
def vapi_callback(data: dict):
    """Handle Vapi call status webhooks - LIVE"""
    from supabase import create_client
    import os
    
    call_status = data.get('message', {}).get('type', 'unknown')
    call_id = data.get('message', {}).get('call', {}).get('id', 'unknown')
    
    print(f"[VAPI-LIVE] {call_status} - Call: {call_id}")
    
    # Deep Brain Harvest
    if call_status == 'end-of-call-report':
        try:
            supa_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            supa_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if supa_url and supa_key:
                client = create_client(supa_url, supa_key)
                msg = data.get('message', {})
                logger_data = {
                    'call_id': msg.get('call', {}).get('id'),
                    'phone_number': msg.get('customer', {}).get('number'),
                    'assistant_id': msg.get('assistantId'),
                    'transcript': msg.get('transcript'),
                    'summary': msg.get('summary'),
                    'sentiment': msg.get('analysis', {}).get('sentiment'),
                    'metadata': msg
                }
                client.table('call_transcripts').upsert(logger_data).execute()
                print(f"[DEEP BRAIN] Harvested call {call_id}")
        except Exception as e:
            print(f"[DEEP BRAIN] Harvest Failed: {e}")
    
    return {"status": "received", "call_status": call_status}

# ============ HEALTH CHECK ============
@app.function(image=image)
@modal.web_endpoint(method="GET", label="health-live")
def health():
    from datetime import datetime
    return {
        "status": "LIVE",
        "service": "Empire Webhooks",
        "timestamp": datetime.now().isoformat()
    }

# ============ LOCAL ENTRYPOINT ============
@app.local_entrypoint()
def main():
    print("🚀 Empire Webhooks Deployed!")
    print("ENDPOINTS:")
    print("  - /vapi-live (POST) - Vapi Callback")
    print("  - /health-live (GET) - Health Check")
