"""
BOARD CALL ROUND 3 - Deep code-level analysis
The website number IS correct. The webhook IS firing. BUT:
1. Line 829 writes to non-existent customer_name column → MAY CRASH before notification
2. The voice call DID log to conversation_logs (20:40 UTC entry exists)
3. But no notification SMS was received by Dan
"""
import requests, os, json, time
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

PROMPT = """BOARD CALL ROUND 3 - We need deeper analysis. Previous fixes didn't fully resolve.

KEY FACTS:
1. Website phone number +18632132505 has CORRECT serverUrl pointing to our webhook
2. Voice call at 20:40 UTC DID get logged to conversation_logs (transcript + summary saved) 
3. Dan DID NOT receive notification SMS after the call
4. The vapi_webhook end-of-call-report handler does this in order:
   a. Extract name from transcript (lines 772-786)
   b. Look up customer_id from customer_memory (lines 790-796)
   c. Insert to conversation_logs (lines 798-809) ← THIS WORKS (proven by 20:40 entry)
   d. Refresh context_summary (lines 811-815)
   e. UPSERT to customer_memory with customer_name field (line 829) ← PROBLEM: customer_name column DOES NOT EXIST on customer_memory table
   f. Notify Dan via GHL webhook (lines 844-874) ← Dan says he NEVER gets this

5. Line 829 has: "customer_name": extracted_name → but the DB table has NO customer_name column
6. The try/except wraps lines 765-840, so a crash at 829 would skip everything after it INCLUDING the notification at line 844
7. The notification code (lines 844-874) is OUTSIDE the try/except that handles the upsert, so it SHOULD still execute even if upsert fails

WAIT - Looking again: Line 844 is INSIDE the same if-block (if caller_phone:) but the notification try sits AFTER the upsert try/except block ends at line 840. So the notification SHOULD execute unless the outer try (line 765) catches first.

Actually the structure is:
```
if caller_phone and (transcript or summary):  # line 764
    try:  # line 765 - START of big try
        ...
        supabase.table("customer_memory").upsert(...)  # line 827 - customer_name crash here?
    except Exception as e:  # line 839
        print(f"WRITE FAILED: {e}")
# NOTE: Notification code at line 844 is OUTSIDE the try/except
# BUT it's still INSIDE the if-block starting at line 764
# So if caller_phone exists AND there's transcript/summary, notification should run
```

SMS ISSUES:
- Dan texted Sarah and got "Hey Michael" at 20:05 UTC (BEFORE our deploy at ~20:14)
- After texting "My name is Daniel", Sarah correctly said "Hey Daniel" 
- But Sarah is STILL asking the authority question every message (looping)
- Also when Dan said "still not working" he may mean ANY of: calls, SMS, or notifications

QUESTIONS:
1. Could the customer_name column crash the upsert silently and skip notification?
2. Is the notification GHL webhook URL even active/working?
3. Why does Sarah still loop on the authority question despite question tracking?
4. What else could prevent Dan from getting the call notification?

Be SPECIFIC about what to check next. Under 300 words."""

grok_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

for name, api_key, api_url, model, is_gemini in [
    ("GROK", grok_key, "https://api.x.ai/v1/chat/completions", "grok-3-mini", False),
    ("CHATGPT", openai_key, "https://api.openai.com/v1/chat/completions", "gpt-4o-mini", False),
]:
    print(f"Calling {name}...")
    try:
        body = {"messages": [{"role": "system", "content": f"You are {name}. Analyze code-level bugs."}, {"role": "user", "content": PROMPT}], "model": model, "temperature": 0.3, "max_tokens": 600}
        r = requests.post(api_url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=body, timeout=60)
        reply = r.json()['choices'][0]['message']['content'] if r.status_code == 200 else f"ERROR {r.status_code}: {r.text[:200]}"
        BOARD_RESPONSES[name] = reply
        log_receipt(name, api_url, r.status_code, json.dumps(body)[:200], r.text[:500])
        print(f"  ✅ {r.status_code}")
    except Exception as e:
        BOARD_RESPONSES[name] = f"EXCEPTION: {e}"

# GEMINI
print("Calling GEMINI...")
try:
    body = {"contents": [{"parts": [{"text": PROMPT}]}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}", headers={"Content-Type": "application/json"}, json=body, timeout=60)
    reply = r.json()['candidates'][0]['content']['parts'][0]['text'] if r.status_code == 200 else f"ERROR {r.status_code}"
    BOARD_RESPONSES["GEMINI"] = reply
    log_receipt("GEMINI", "googleapis.com", r.status_code, json.dumps(body)[:200], r.text[:500])
    print(f"  ✅ {r.status_code}")
except Exception as e:
    BOARD_RESPONSES["GEMINI"] = f"EXCEPTION: {e}"

# ANTIGRAVITY
BOARD_RESPONSES["ANTIGRAVITY"] = """Code analysis:
1. The upsert at line 827-832 writes customer_name which doesn't exist. BUT Supabase PostgREST upsert with non-existent columns returns 400 error, not a crash. The outer try/except at line 765 catches this, prints error, and execution continues to notification at line 844.
2. The REAL question: Does the GHL webhook at line 861 actually send SMS? We need to test this webhook URL directly.
3. SMS looping: questions_asked tracking was just deployed but won't help until the PROMPT is updated to actually CHECK questions_asked before asking them. The system prompt (lines 694-713) still lists all 5 BANT questions with no condition to skip already-asked ones.
4. RECOMMENDATION: (a) Test the GHL notification webhook directly, (b) Inject questions_asked into Sarah's prompt so she skips already-asked ones."""

with open('scripts/board3_responses.txt', 'w', encoding='utf-8') as f:
    for m, r in BOARD_RESPONSES.items():
        f.write(f"\n{'='*50}\n{m}\n{'='*50}\n{r}\n")
with open('scripts/board3_receipts.txt', 'w', encoding='utf-8') as f:
    f.write(f"BOARD CALL 3 RECEIPTS - {datetime.now().isoformat()}\n")
    for r in RECEIPTS:
        f.write(f"\n--- {r['board_member']} ---\nTimestamp: {r['timestamp']}\nEndpoint: {r['endpoint']}\nHTTP: {r['http_status']}\nRequest: {r['request_preview']}\nResponse: {r['response_preview']}\n")

print(f"\n✅ Board call 3 complete. {len(RECEIPTS)} API calls logged.")
