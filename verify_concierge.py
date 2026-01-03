
import requests
import re
import time
import os

LOG_PATH = "deploy_final.log"

def get_endpoint_url():
    print("🔍 Scanning log for concierge_chat endpoint...")
    if not os.path.exists(LOG_PATH):
        print("❌ Log file not found.")
        return None
        
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Regex to find: ├── 🔨 Created web function concierge_chat => \n\│   (URL)
    match = re.search(r"concierge_chat =>\s+[│\s]+(https://[a-zA-Z0-9-]+\.modal\.run)", content)
    if match:
        return match.group(1).strip()
    return None

def test_endpoint(url):
    print(f"🚀 Testing Concierge: {url}")
    
    # Test 1: General Support
    payload1 = {
        "message": "How do I reset my password?",
        "user_context": {"plan": "Starter"}
    }
    try:
        res = requests.post(url, json=payload1)
        print(f"📝 Test 1 (Support): {res.json().get('reply')}")
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")

    # Test 2: Upsell Trigger
    payload2 = {
        "message": "What is the price for the office manager voice agent?",
        "user_context": {"plan": "Growth"}
    }
    try:
        res = requests.post(url, json=payload2)
        data = res.json()
        print(f"📝 Test 2 (Upsell): Action={data.get('action')}")
        if data.get('action') == "show_quote":
            quote = data.get('data', {})
            print(f"   💰 Quote Generated: Total Monthly=${quote.get('total_monthly')}")
            print(f"   📋 Items: {[i['name'] for i in quote.get('items', [])]}")
        else:
            print(f"   ⚠️ Expected 'show_quote', got {data.get('action')}")
            
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")

if __name__ == "__main__":
    url = get_endpoint_url()
    if url:
        test_endpoint(url)
    else:
        print("⚠️ Endpoint URL not found in logs yet. (Deployment might be ongoing)")
