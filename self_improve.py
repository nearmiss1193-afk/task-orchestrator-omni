"""
Self-Improvement Analysis - Review interactions and suggest improvements
"""
import requests
import json

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# Get last 50 interactions
r = requests.get(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, params={"order": "created_at.desc", "limit": 50})
interactions = r.json() if r.status_code == 200 else []
print(f"Found {len(interactions)} interactions")

# Get objections from memories
r2 = requests.get(f"{SUPABASE_URL}/rest/v1/memories", headers=headers, params={"memory_type": "eq.objection", "limit": 20})
objections = r2.json() if r2.status_code == 200 else []
print(f"Found {len(objections)} objections logged")

# Analyze with Gemini
batch = json.dumps([{"intent": i.get("intent"), "outcome": i.get("outcome"), "escalated": i.get("escalated")} for i in interactions[:30]])
objection_list = [o.get("value","")[:50] for o in objections[:5]]

prompt = f"""Analyze these {len(interactions)} sales interactions and return improvement suggestions.

Interactions: {batch}
Objections logged: {objection_list}

Goal: increase booking rate and reduce escalations while staying compliant.
Hard rule: do not change pricing/guarantees/policies without human approval.

Return ONLY valid JSON with this structure:
{{
  "top_objections": ["objection 1", "objection 2"],
  "top_failure_modes": [{{"pattern":"what failed", "fix":"how to fix"}}],
  "kb_gaps": [{{"question":"unanswered question", "recommended_answer":"suggested answer"}}],
  "script_updates": [{{"where":"sms_opening or pricing or booking_cta or call_flow", "change":"suggested change", "risk":"low or med or high"}}],
  "experiments": [{{"name":"test name", "a":"variant a", "b":"variant b", "metric":"booking_rate"}}]
}}"""

r = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
    headers={"Content-Type": "application/json"},
    json={"contents": [{"parts": [{"text": prompt}]}]},
    timeout=60
)

if r.status_code == 200:
    result = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    # Clean up markdown if present
    if "```json" in result:
        result = result.split("```json")[1].split("```")[0]
    elif "```" in result:
        result = result.split("```")[1].split("```")[0]
    print("\n" + "=" * 60)
    print("SELF-IMPROVEMENT ANALYSIS")
    print("=" * 60)
    print(result)
    
    # Save to playbook_updates
    try:
        data = json.loads(result)
        for update in data.get("script_updates", []):
            requests.post(
                f"{SUPABASE_URL}/rest/v1/playbook_updates",
                headers={**headers, "Content-Type": "application/json"},
                json={
                    "update_type": "script_change",
                    "where_applies": update.get("where"),
                    "change_description": update.get("change"),
                    "risk_level": update.get("risk"),
                    "status": "proposed"
                }
            )
        print(f"\nSaved {len(data.get('script_updates', []))} suggestions to playbook_updates")
    except:
        pass
else:
    print(f"Gemini error: {r.status_code}")
    print(r.text)
