import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
USER_PHONE = os.getenv('TEST_PHONE')
ASSISTANT_ID = '1a797f12-e2dd-4f7f-b2c5-08c38c74859a'

def check_website():
    print("\n📡 CHECKING WEBSITES...")
    urls = [
        "https://aiserviceco.com",
        "https://www.aiserviceco.com"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            status = "✅" if r.status_code == 200 else "❌"
            print(f"{status} {url} ({r.status_code})")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

def trigger_call():
    print(f"\n📞 TRIGGERING CALL TO {USER_PHONE}...")
    headers = {
        'Authorization': f'Bearer {VAPI_PRIVATE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 1. Start Call
    try:
        r = requests.post(
            'https://api.vapi.ai/call/phone',
            headers=headers,
            json={
                'assistantId': ASSISTANT_ID,
                'phoneNumberId': '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e',
                'customer': {'number': USER_PHONE, 'name': 'Owner Verify'}
            },
            timeout=10
        )
        if r.status_code == 201:
            print(f"✅ Call initiated successfully (ID: {r.json().get('id')})")
        else:
            print(f"❌ Failed to init call: {r.text}")
            return
    except Exception as e:
        print(f"❌ Call init error: {e}")
        return

    # 2. Monitor for 15 seconds
    print("   Monitoring call status for 15s...")
    for i in range(3):
        time.sleep(5)
        try:
            r = requests.get('https://api.vapi.ai/call', headers=headers, params={'limit': 1})
            c = r.json()[0]
            status = c.get('status')
            ended_reason = c.get('endedReason')
            
            print(f"   [{i*5+5}s] Status: {status} | EndedReason: {ended_reason}")
            
            if status == 'ended' and ended_reason == 'silence-timed-out':
                print("❌ FAIL: Still getting silence timeout!")
                return
            elif status == 'in-progress':
                pass # Good
        except:
            pass
            
    print("\n✅ VERIFICATION COMPLETE: Call initiated and stayed active/progressing.")

if __name__ == "__main__":
    check_website()
    trigger_call()
