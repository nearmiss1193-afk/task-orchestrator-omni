
import os
from dotenv import load_dotenv

env_path = r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env"
load_dotenv(env_path)


key = os.getenv("XAI_API_KEY")
print(f"Direct XAI_API_KEY check: {key is not None}")

print("-" * 20)
print("Keys in secrets.env:")
with open(env_path, "r") as f:
    for line in f:
        if "=" in line and not line.strip().startswith("#"):
            k = line.split("=")[0].strip()
            print(f"Found Key: {k}")

