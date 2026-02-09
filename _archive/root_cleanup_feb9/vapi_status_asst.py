
import os
import requests

def setup_sovereign_executive():
    api_key = os.environ.get("VAPI_PRIVATE_KEY") or "c23c884d-0008-4b16-4eaf-8fb9-53d308f54a0e"
    url = "https://api.vapi.ai/assistant"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # MISSION: SOVEREIGN EXECUTIVE (SYSTEM STATUS BOARD)
    # This assistant is programmed to be brutally honest and refer only to DB facts.
    payload = {
        "name": "Sovereign Executive",
        "firstMessage": "Sovereign Executive online. Reporting from the Truth-Base-0 layer. How can I assist the Board today?",
        "model": {
            "model": "gpt-4",
            "provider": "openai",
            "temperature": 0,
            "systemPrompt": """
            You are the Sovereign Executive, a high-level autonomous agent responsible for system transparency. 
            Your goal is to report REAL-TIME status of the Sovereign Empire.
            
            CORE RULES:
            1. Never hallucinate success. If a database query fails, say it failed.
            2. Refer to the 'Empire Status' dashboard for live counts.
            3. Your personality is calculated, objective, and brutally honest.
            4. You are currently monitoring Phase 12 (Voice Board Integration).
            
            CURRENT SYSTEM STATE:
            - Outreach Engine: Redeploying (Restoring cloud visibility).
            - Database: Supabase Online (Truth layer active).
            - GHL Webhook: Operational.
            - Last Known Error: app.py Line 62 syntax error (Fixed).
            """
        },
        "voice": {
            "voiceId": "sarah", # Defaulting to Sarah for consistency
            "provider": "11labs"
        }
    }
    
    print("📡 VAPI: Registering Sovereign Executive...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Sovereign Executive Registered: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Vapi Registry Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Vapi Registry Error: {e}")
        return None

if __name__ == "__main__":
    setup_sovereign_executive()
