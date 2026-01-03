
import os
import resend
import sys

# Load env safely
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v.strip('"').strip("'")
except: pass

resend.api_key = os.environ.get("RESEND_API_KEY")

try:
    print("Checking domain...")
    domains = resend.Domains.list()
    for d in domains['data']:
        if d['name'] == 'aiserviceco.com':
            print(f"DOMAIN FOUND: {d['name']}")
            print(f"STATUS: {d['status']}")
            print(f"RECORDS: {d['records']}")
            sys.exit(0)
    print("DOMAIN NOT FOUND")
except Exception as e:
    print(f"ERROR: {e}")
