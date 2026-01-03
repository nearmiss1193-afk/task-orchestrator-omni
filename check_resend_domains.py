import os
import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.environ.get("RESEND_API_KEY", "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy")

print("🔍 Checking Resend Domains...")
try:
    domains = resend.Domains.list()
    if not domains.get('data'):
        print("⚠️ No domains found. You must add 'aiserviceco.com' to Resend.")
    else:
        for d in domains['data']:
            print(f"\n🌐 Domain: {d['name']} (ID: {d['id']})")
            print(f"   Status: {d['status']}")
            
            # Get DNS Records
            if d['status'] != 'verified':
                domain_details = resend.Domains.get(d['id'])
                print("   ⚠️ VERIFICATION REQUIRED. Add these records:")
                with open("DNS_RECORDS.txt", "w", encoding="utf-8") as f:
                    f.write(f"DOMAIN VERIFICATION FOR: {d['name']}\n")
                    f.write("Add these records to your DNS Provider (GoDaddy, Namecheap, etc):\n\n")
                    for record in domain_details.get('records', []):
                        line = f"Type: {record['record']}\nName: {record['name']}\nValue: {record['value']}\nStatus: {record['status']}\n---\n"
                        print(line)
                        f.write(line + "\n")

except Exception as e:
    print(f"❌ Error listing domains: {e}")
