import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('.env.local')

gemini_key = os.environ.get('GEMINI_API_KEY')
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

cmd = [
    'python', '-m', 'modal', 'secret', 'create', 'agency-vault', '--force',
    f'GEMINI_API_KEY={gemini_key}',
    f'SUPABASE_URL={supabase_url}',
    f'SUPABASE_KEY={supabase_key}',
]

for k in ['OPENAI_API_KEY', 'RESEND_API_KEY', 'ELEVENLABS_API_KEY', 'VAPI_API_KEY', 'GOOGLE_API_KEY', 'GOOGLE_CSE_ID', 'ABACUS_API_KEY']:
    val = os.environ.get(k)
    if val:
        cmd.append(f'{k}={val}')

print("Updating secret with --force...")
res1 = subprocess.run(cmd, capture_output=True, text=True)
if res1.returncode != 0:
    print("Secret update failed:", res1.stderr)
else:
    print("Secret updated successfully!")
    print("Deploying Modal app...")
    res2 = subprocess.run(['python', '-m', 'modal', 'deploy', 'deploy.py'], capture_output=True, text=True)
    if res2.returncode != 0:
        print("Deploy failed:", res2.stderr)
        print("STDOUT:", res2.stdout)
    else:
        print("Deploy successful!")
        print(res2.stdout)
