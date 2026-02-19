"""Check and set Vapi server URL on Sarah's assistant for call notifications"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]

SARAH_ID = "ae717f29-6542-422f-906f-ee7ba6fa0bfe"
MODAL_WEBHOOK = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

# Check Sarah's current server URL
r = requests.get(
    f"https://api.vapi.ai/assistant/{SARAH_ID}",
    headers={"Authorization": f"Bearer {key}"}
)
d = r.json()
current_server = d.get("serverUrl", "NONE")
print(f"Current serverUrl: {current_server}")
print(f"Has serverUrl: {'serverUrl' in d}")

# Set the server URL so Vapi sends end-of-call-report to our Modal webhook
update = {
    "serverUrl": MODAL_WEBHOOK
}

r2 = requests.patch(
    f"https://api.vapi.ai/assistant/{SARAH_ID}",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=update
)
print(f"Sarah serverUrl update: {r2.status_code}")

# Also check Sarah the Spartan (second assistant)
SARAH2_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
r3 = requests.get(
    f"https://api.vapi.ai/assistant/{SARAH2_ID}",
    headers={"Authorization": f"Bearer {key}"}
)
d3 = r3.json()
print(f"\nSarah Spartan serverUrl: {d3.get('serverUrl', 'NONE')}")

r4 = requests.patch(
    f"https://api.vapi.ai/assistant/{SARAH2_ID}",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"serverUrl": MODAL_WEBHOOK}
)
print(f"Sarah Spartan serverUrl update: {r4.status_code}")

# Also check Rachel
RACHEL_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"
r5 = requests.patch(
    f"https://api.vapi.ai/assistant/{RACHEL_ID}",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"serverUrl": MODAL_WEBHOOK}
)
print(f"Rachel serverUrl update: {r5.status_code}")

# Verify the phone number also has server URL
print("\nChecking phone numbers for server URL...")
r6 = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {key}"})
nums = r6.json()
for n in nums:
    name = n.get("name", "")
    number = n.get("number", "")
    srv = n.get("serverUrl", "NONE")
    asst = n.get("assistantId", "NONE")[:12] if n.get("assistantId") else "NONE"
    print(f"  {name} ({number}): serverUrl={srv}, assistant={asst}")
