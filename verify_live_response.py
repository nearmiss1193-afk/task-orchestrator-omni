import time
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Configuration
GHL_TOKEN = os.environ.get("GHL_API_TOKEN")
GHL_LOC = os.environ.get("GHL_LOCATION_ID")
# The simulation sends "Yes" to Sarah. We expect "demo" or a booking link in reply.
EXPECTED_KEYWORDS = ["demo", "calendar", "book", "link", "schedule"]

def verify_latest_response():
    print("🕵️ MONITORING GHL FOR AI RESPONSE...")
    
    headers = {
        "Authorization": f"Bearer {GHL_TOKEN}",
        "Version": "2021-07-28"
    }
    
    # Poll for 45 seconds
    start_time = time.time()
    while time.time() - start_time < 45:
        try:
            url = f"https://services.leadconnectorhq.com/conversations/search?locationId={GHL_LOC}&sort=desc&limit=3"
            res = requests.get(url, headers=headers)
            
            if res.status_code == 200:
                conversations = res.json().get('conversations', [])
                for conv in conversations:
                    # Look for the simulation conversation (Contact Name usually 'Sovereign User' or similar from simulation)
                    # Or just look for ANY recent outbound message containing keywords
                    
                    last_msg = conv.get('lastMessageBody', '').lower()
                    direction = conv.get('lastMessageDirection', '')
                    
                    if direction == "outbound" and any(k in last_msg for k in EXPECTED_KEYWORDS):
                        print(f"\n✅ VERIFIED: AI Replied!")
                        print(f"   Message: '{conv.get('lastMessageBody')}'")
                        print(f"   Contact: {conv.get('contactName')}")
                        return True
                        
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(2)
            
        except Exception as e:
            print(f"Error: {e}")
            
    print("\n❌ VERIFICATION FAILED: No AI response detected within timeout.")
    return False

if __name__ == "__main__":
    success = verify_latest_response()
    if not success:
        sys.exit(1)
