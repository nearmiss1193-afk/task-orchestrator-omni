
import requests
import time

URL = "https://empire-unified-backup-production.up.railway.app/vapi/webhook"
FAKE_CALL_ID = f"test-call-{int(time.time())}"

payload = {
    "message": {
        "type": "end-of-call-report",
        "call": {
            "id": FAKE_CALL_ID,
            "customer": {
                "number": "+15550009999",
                "name": "Test User"
            },
            "assistantId": "test-assistant"
        },
        "analysis": {
            "summary": "This is a test summary from the verification script.",
            "sentiment": "neutral",
            "successEvaluation": "true"
        },
        "transcript": "User: Hello? AI: Hi, this is a test.",
        "recordingUrl": "http://example.com/rec.mp3",
        "cost": 0.05,
        "endedReason": "completed"
    }
}

print(f"Sending mock webhook to {URL}...")
try:
    r = requests.post(URL, json=payload, timeout=10)
    print(f"Status: {r.status_code}")
    print(r.text)
except Exception as e:
    print(e)
