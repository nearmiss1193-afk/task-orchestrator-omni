
import requests
import re
import time
import os

LOG_PATH = "deploy_final.log"

def get_endpoint_url():
    print("🔍 Scanning log for office_voice_tool endpoint...")
    if not os.path.exists(LOG_PATH):
        print("❌ Log file not found.")
        return None
        
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Look for: ├── 🔨 Created web function office_voice_tool => \n\│   (URL)
    # The log format shows the URL on the next line or same line depending on width
    # Regex to find the URL structure
    match = re.search(r"office_voice_tool =>\s+[│\s]+(https://[a-zA-Z0-9-]+\.modal\.run)", content)
    if match:
        return match.group(1).strip()
    return None

def test_endpoint(url):
    print(f"🚀 Testing Endpoint: {url}")
    
    # Test 1: Check Inventory (Should return not found or empty initially)
    payload1 = {
        "tool": "check_inventory",
        "args": {"item": "paper_test_v1"}
    }
    try:
        res = requests.post(url, json=payload1)
        print(f"📝 Test 1 (Check): {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")

    # Test 2: Add Inventory
    payload2 = {
        "tool": "update_inventory",
        "args": {"item": "paper_test_v1", "quantity": "50", "operation": "add"}
    }
    try:
        res = requests.post(url, json=payload2)
        print(f"📝 Test 2 (Add): {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")

    # Test 3: Check Again
    try:
        res = requests.post(url, json=payload1)
        print(f"📝 Test 3 (Check Updated): {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Test 3 Failed: {e}")

if __name__ == "__main__":
    url = get_endpoint_url()
    if url:
        test_endpoint(url)
    else:
        print("⚠️ Could not find endpoint URL in logs yet.")
