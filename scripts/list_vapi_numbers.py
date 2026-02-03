import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.environ.get("VAPI_PRIVATE_KEY")
SALES_ID = os.environ.get("VAPI_PHONE_NUMBER_ID")

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

print(f"🔍 Listing Vapi Numbers (excluding Sales ID: {SALES_ID})...")

try:
    resp = requests.get("https://api.vapi.ai/phone-number", headers=headers)
    if resp.status_code == 200:
        numbers = resp.json()
        found_spare = False
        for ph in numbers:
            print(f"DEBUG RAW: {ph}") # Allow user to see structure
            num = ph.get('number') or ph.get('phoneNumber') or "UNKNOWN"
            pid = ph.get('id')
            
            is_sales = (pid == SALES_ID)
            tag = "[SALES/ACTIVE]" if is_sales else "[SPARE/AVAILABLE]"
            print(f"📱 {num} (ID: {pid}) {tag}")
            
            if not is_sales:
                found_spare = True
        
        if not found_spare:
            print("❌ No spare numbers found.")
    else:
        print(f"❌ Error: {resp.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
