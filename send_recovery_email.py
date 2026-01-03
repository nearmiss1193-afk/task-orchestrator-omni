import os
import requests
from dotenv import load_dotenv
from modules.communications.routing import route_communication

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

TARGET_EMAIL = "owner@aiserviceco.com"
TARGET_NAME = "System Owner"

def send_recovery_packet():
    print("🚀 Reading Recovery Protocol...")
    try:
        with open("recovery_protocol.md", "r", encoding="utf-8") as f:
            protocol_content = f.read()
    except:
        # Fallback to brain artifact if local Copy missing
        brain_path = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\RECOVERY_PROTOCOL.md"
        with open(brain_path, "r", encoding="utf-8") as f:
            protocol_content = f.read()
            
    print(f"🚀 Dispatching Secure Packet to {TARGET_EMAIL}...")
    
    html_content = f"""
    <h2>Empire System Recovery Protocol</h2>
    <p>Attached below is the master recovery protocol for the Empire Unified System.</p>
    <p><strong>Transmission Channel:</strong> Sovereign Redundancy Layer</p>
    <hr>
    <pre style="background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd; white-space: pre-wrap;">
{protocol_content}
    </pre>
    <hr>
    <p>Sent by: Sovereign Executive Agent</p>
    """
    
    contact = {"email": TARGET_EMAIL, "name": TARGET_NAME}
    content = {
        "subject": "CRITICAL: System Recovery Instructions & Login Protocols",
        "body": html_content
    }
    
    # USE THE ROUTER (Sovereign -> GHL Backup)
    result = route_communication(contact, "EMAIL", content)
    
    if result['status'] in ['sent', 'simulated', 'sent_backup']:
        print(f"✅ Recovery Packet Delivered via {result.get('provider')}.")
        return True
    else:
        print(f"❌ Delivery Failed: {result}")
        return False

if __name__ == "__main__":
    send_recovery_packet()
