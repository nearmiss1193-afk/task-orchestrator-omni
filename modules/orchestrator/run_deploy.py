import subprocess
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

env = os.environ.copy()
# Ensure Modal hears them
env["MODAL_TOKEN_ID"] = os.environ.get("MODAL_TOKEN_ID")
env["MODAL_TOKEN_SECRET"] = os.environ.get("MODAL_TOKEN_SECRET")

print(f"Deploying with Token ID: {env.get('MODAL_TOKEN_ID')}")

try:
    result = subprocess.run(
        ["python", "-m", "modal", "deploy", "deploy.py"],
        env=env,
        capture_output=True,
        text=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
except Exception as e:
    print("Deployment crashed:", e)
