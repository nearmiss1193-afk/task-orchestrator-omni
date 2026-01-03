import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
# Using the same ID as Rachael to instantly upgrade the Dashboard button
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

# Read the Orchestrator Prompt from the Artifact
PROMPT_PATH = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\ORCHESTRATOR_PROMPT.md"

try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        ORCHESTRATOR_SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    print("❌ Critical: ORCHESTRATOR_PROMPT.md not found!")
    exit(1)

FIRST_MESSAGE = "Antigravity Online. Level 5 Connection Established. Awaiting your command."

def upgrade_assistant():
    print(f"🔼 Upgrading Assistant {ASSISTANT_ID} to ORCHESTRATOR (Level 5)...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-4-turbo", # Upgrade to GPT-4 for Orchestrator intelligence
            "systemPrompt": ORCHESTRATOR_SYSTEM_PROMPT,
            "messages": [
                {
                    "content": ORCHESTRATOR_SYSTEM_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE,
        "name": "Antigravity (Orchestrator)",
        "voice": {
             "provider": "11labs",
             "voiceId": "onwK4e9ZLuTAKqWW03F9" # Daniel (Deep/Authoritative) - Change if desired
        }
    }
    
    try:
        res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
        res.raise_for_status()
        print("✅ SUCCESS: Assistant Upgraded to 'Antigravity (Orchestrator)'.")
        print("   - Voice: Daniel (Deep/Authoritative)")
        print("   - Model: GPT-4 Turbo")
        print("   - Clearance: Level 5")
    except Exception as e:
        print(f"❌ FAILED to upgrade assistant: {e}")
        if 'res' in locals():
            print(res.text)

if __name__ == "__main__":
    upgrade_assistant()
