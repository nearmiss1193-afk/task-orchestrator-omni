"""Board Call Round 4 - THE SMOKING GUN"""
import requests, os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

RECEIPTS = []
BOARD_RESPONSES = {}

def log_receipt(member, endpoint, status, req_preview, resp_preview):
    RECEIPTS.append({"timestamp": datetime.now().isoformat(), "board_member": member,
                     "endpoint": endpoint, "http_status": status,
                     "request_preview": req_preview[:200], "response_preview": resp_preview[:500]})

PROMPT = """BOARD CALL ROUND 4 - ROOT CAUSE FOUND

SMOKING GUN EVIDENCE (from Vapi API direct query):

1. Assistant config (1a797f12): serverMessages = ['end-of-call-report', 'status-update', 'hang', 'speech-update', 'transcript', 'function-call', 'assistant.started', 'conversation-update'] ← HAS end-of-call-report ✅

2. BUT every actual CALL shows: serverMessages: [] (EMPTY ARRAY)
   - Call at 21:03 → serverMessages: []
   - Call at 20:40 → serverMessages: []
   - Call at 19:56 → serverMessages: []
   - Call at 19:54 → serverMessages: []

3. Phone +18632132505 config: serverMessages (phone-level): NOT SET

4. vapi_debug_logs in last 60 min: ZERO entries (no assistant-request events either!)

5. BUT conversation_logs HAS two voice entries at 20:41 and 21:04 (from end-of-call-report)

WAIT - that's contradictory. If serverMessages is empty, how did conversation_logs get voice entries? 

Possible explanation: The conversation_logs entries could have been created by assistant-request event (which returns assistantOverrides), not by end-of-call-report. Let me re-read the code...

Actually looking at the conversation_logs entries: they have "Call summary: Joe from AAA Tire..." WHICH IS the end-of-call-report summary. So end-of-call-report IS being received somehow, and the conversation_logs INSERT succeeds.

BUT the notification STILL doesn't fire. This means either:
A. The code DOES reach the notification block but the GHL webhook silently fails
B. The customer_name crash (now fixed) was killing it before notification, but the NEW deploy hasn't been tested with a call yet
C. End-of-call-report was received for EARLIER calls (before our deploy) but not for Dan's latest call after our deploy

CRITICAL QUESTION: Dan's latest call was at 21:03 UTC. Our deploy was at ~21:00 UTC. Did the new code process that call, or was it still running old code?

The conversation_log entry at 21:04 (1 min after the call started at 21:03) suggests the old code processed it because Modal may have had a stale container.

QUESTIONS FOR BOARD:
1. Is the empty serverMessages[] on calls a Vapi API display issue, or does it actually mean no events are sent?
2. Given that conversation_logs HAS voice entries with call summaries, is end-of-call-report actually being received?
3. If it IS being received, and our customer_name crash fix was deployed at ~21:00, did Dan's 21:03 call use the NEW or OLD code?
4. Should Dan make ONE MORE test call to verify with the guaranteed-new code?

Under 200 words."""

grok_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

for name, api_key, api_url, model in [
    ("GROK", grok_key, "https://api.x.ai/v1/chat/completions", "grok-3-mini"),
    ("CHATGPT", openai_key, "https://api.openai.com/v1/chat/completions", "gpt-4o-mini"),
]:
    print(f"Calling {name}...")
    try:
        body = {"messages": [{"role": "system", "content": f"You are {name}. Analyze Vapi webhook issues."}, {"role": "user", "content": PROMPT}], "model": model, "temperature": 0.3, "max_tokens": 400}
        r = requests.post(api_url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=body, timeout=60)
        reply = r.json()['choices'][0]['message']['content'] if r.status_code == 200 else f"ERROR {r.status_code}: {r.text[:200]}"
        BOARD_RESPONSES[name] = reply
        log_receipt(name, api_url, r.status_code, json.dumps(body)[:200], r.text[:500])
        print(f"  ✅ {r.status_code}")
    except Exception as e:
        BOARD_RESPONSES[name] = f"EXCEPTION: {e}"

print("Calling GEMINI...")
try:
    body = {"contents": [{"parts": [{"text": PROMPT}]}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}", headers={"Content-Type": "application/json"}, json=body, timeout=60)
    reply = r.json()['candidates'][0]['content']['parts'][0]['text'] if r.status_code == 200 else f"ERROR {r.status_code}"
    BOARD_RESPONSES["GEMINI"] = reply
    log_receipt("GEMINI", "googleapis.com", r.status_code, json.dumps(body)[:200], r.text[:500])
    print(f"  ✅ {r.status_code}")
except Exception as e:
    BOARD_RESPONSES["GEMINI"] = f"EXCEPTION: {e}"

BOARD_RESPONSES["ANTIGRAVITY"] = """DIRECT ANALYSIS:
1. The conversation_logs entries with "Call summary: Joe from AAA Tire" PROVE end-of-call-report IS being received
2. BUT vapi_debug_logs has ZERO entries in 60 min — means the code path that logs to debug table (assistant-request handler) is NOT firing
3. The end-of-call-report handler writes to conversation_logs (works) then does customer_memory upsert (crashed on customer_name) then notification (never reached)
4. Our fix removed customer_name at ~21:00 UTC. Dan's call was at 21:03. Modal containers may have been stale.
5. RECOMMENDATION: Dan should make ONE MORE test call now (at least 10 min after deploy) to guarantee the new code runs.
6. If it STILL fails, the GHL webhook is the remaining suspect."""

with open('scripts/board4_responses.txt', 'w', encoding='utf-8') as f:
    for m, r in BOARD_RESPONSES.items():
        f.write(f"\n{'='*50}\n{m}\n{'='*50}\n{r}\n")
with open('scripts/board4_receipts.txt', 'w', encoding='utf-8') as f:
    f.write(f"BOARD CALL 4 RECEIPTS - {datetime.now().isoformat()}\n")
    for r in RECEIPTS:
        f.write(f"\n--- {r['board_member']} ---\nTimestamp: {r['timestamp']}\nEndpoint: {r['endpoint']}\nHTTP: {r['http_status']}\nRequest: {r['request_preview']}\nResponse: {r['response_preview']}\n")

print(f"\n✅ Board call 4 complete. {len(RECEIPTS)} API calls logged.")
