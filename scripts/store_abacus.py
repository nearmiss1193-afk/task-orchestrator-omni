import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('.env.local')

abacus_key = "s2_5e015f3b677c4881959e434fe0761fef"

cmd = [
    'python', '-m', 'modal', 'secret', 'create', 'agency-vault', '--force',
    f'ABACUS_API_KEY={abacus_key}'
]

# Ensure we grab EXACTLY the keys the workers need
keys_to_sync = [
    'OPENAI_API_KEY', 
    'RESEND_API_KEY', 
    'ELEVENLABS_API_KEY', 
    'VAPI_PRIVATE_KEY',     # CRITICAL: This was missing!
    'VAPI_PHONE_NUMBER_ID', # CRITICAL: This was missing!
    'GOOGLE_API_KEY', 
    'GOOGLE_CSE_ID', 
    'GEMINI_API_KEY', 
    'SUPABASE_URL', 
    'SUPABASE_KEY',
    'NEXT_PUBLIC_SUPABASE_URL',
    'SUPABASE_SERVICE_ROLE_KEY'
]

for k in keys_to_sync:
    val = os.environ.get(k)
    # Handle Supabase aliases
    if k == 'SUPABASE_URL' and not val:
        val = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
    if k == 'SUPABASE_KEY' and not val:
        val = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        
    if val:
        cmd.append(f'{k}={val}')

print("Updating secret with --force to store Abacus key and restore Vapi keys...")
res1 = subprocess.run(cmd, capture_output=True, text=True)
if res1.returncode != 0:
    print("Secret update failed:", res1.stderr)
else:
    print("Secret updated successfully!")
