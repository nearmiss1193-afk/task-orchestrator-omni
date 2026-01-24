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
    "GHL_LOCATION_ID": os.environ.get("GHL_LOCATION_ID"),
    "VAPI_PRIVATE_KEY": "c23c884d-0008-4b14-ad5d-530e98d0c9da",
    "VAPI_ASSISTANT_ID": "dd975344-df1b-4e50-857b-735feacb8bd0",
    "VAPI_PUBLIC_KEY": "3b065ff0-a721-4b66-8255-30b6b8d6daab",
    "STRIPE_SECRET_KEY": "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",
    "STRIPE_WEBHOOK_SECRET": "whsec_1tjSpGjSOCaDetZH5WPfBr0EiIYQt1s6"
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
