import os
import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.environ.get("RESEND_API_KEY", "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy")

print("🌐 Registering Domain: aiserviceco.com...")
try:
    domain = resend.Domains.create({
        "name": "aiserviceco.com"
    })
    print(f"✅ Domain Added! ID: {domain['id']}")
    
    # Get Records
    print("\n⚠️ ACTION REQUIRED: Add these DNS Records:")
    for record in domain['records']:
        print(f"   - Type: {record['record']}")
        print(f"     Name: {record['name']}")
        print(f"     Value: {record['value']}")
        print("     ---")

except Exception as e:
    print(f"❌ Error adding domain: {e}")
