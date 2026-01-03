import subprocess
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

env = os.environ.copy()
env["MODAL_TOKEN_ID"] = os.environ.get("MODAL_TOKEN_ID")
env["MODAL_TOKEN_SECRET"] = os.environ.get("MODAL_TOKEN_SECRET")

# Secrets to add
secrets = {
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
    "SUPABASE_URL": os.environ.get("NEXT_PUBLIC_SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
    "GHL_PRIVATE_KEY": os.environ.get("GHL_PRIVATE_KEY"),
    "GHL_LOCATION_ID": os.environ.get("GHL_LOCATION_ID")
}

cmd = ["python", "-m", "modal", "secret", "create", "agency-vault"]
for k, v in secrets.items():
    cmd.append(f"{k}={v}")

print("Creating secret 'agency-vault'...")
try:
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
except Exception as e:
    print("Secret creation failed:", e)
