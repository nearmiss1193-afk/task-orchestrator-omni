"""Save critical infrastructure config to Supabase - NEVER ASK USER AGAIN"""
from supabase import create_client

url = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'
sb = create_client(url, key)

# CRITICAL INFRASTRUCTURE - NEVER ASK USER AGAIN
configs = [
    {'key': 'HOSTING_PROVIDER', 'status': 'Vercel', 'notes': 'User confirmed Feb 4 2026: Has been on Vercel forever'},
    {'key': 'DOMAIN_REGISTRAR', 'status': 'Squarespace', 'notes': 'Domain hosted by Squarespace, DNS points to Vercel'},
    {'key': 'PRODUCTION_DOMAIN', 'status': 'aiserviceco.com', 'notes': 'THE ONLY DOMAIN TO VERIFY - NOT netlify subdomain'},
    {'key': 'DEPLOY_COMMAND', 'status': 'vercel --prod --yes', 'notes': 'Run from public/ directory'},
    {'key': 'STAGING_DOMAIN', 'status': 'aiserviceco-empire.netlify.app', 'notes': 'STAGING ONLY - do not verify as production'},
    {'key': 'HARD_RULE_verify_prod', 'status': 'ALWAYS verify aiserviceco.com NOT netlify subdomain', 'notes': 'HARD RULE - Feb 4 2026'},
]

for cfg in configs:
    try:
        result = sb.table('system_state').upsert(cfg, on_conflict='key').execute()
        print(f"Saved: {cfg['key']} = {cfg['status']}")
    except Exception as e:
        print(f"Failed: {cfg['key']} - {str(e)[:50]}")

print("\n=== INFRASTRUCTURE CONFIG SAVED TO SUPABASE ===")
