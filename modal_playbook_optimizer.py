"""
NIGHTLY PLAYBOOK OPTIMIZER - Runs every night to suggest improvements
Deployed as Modal scheduled function
"""
import modal
import json
from datetime import datetime

app = modal.App("playbook-optimizer")

image = modal.Image.debian_slim(python_version="3.11").pip_install("requests")

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"


@app.function(image=image, schedule=modal.Cron("0 3 * * *"), timeout=300)  # Run at 3am daily
def run_nightly_optimizer():
    """
    Nightly job: Playbook Optimizer
    - Reads last 50 interactions
    - Outputs 3 script improvements + 1 KB gap
    - Writes to playbook_updates
    - Does NOT auto-apply high-risk changes
    """
    import requests
    
    HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    print("=" * 60)
    print(f"NIGHTLY PLAYBOOK OPTIMIZER - {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    # Get last 50 interactions
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/interactions",
        headers=HEADERS,
        params={"order": "created_at.desc", "limit": 50}
    )
    
    if r.status_code != 200:
        print(f"[ERROR] Failed to get interactions: {r.status_code}")
        return {"error": "Failed to get interactions"}
    
    interactions = r.json()
    print(f"[DATA] Analyzing {len(interactions)} interactions")
    
    if len(interactions) < 5:
        print("[SKIP] Not enough interactions to analyze")
        return {"status": "skipped", "reason": "Not enough data"}
    
    # Prepare batch for AI
    batch = json.dumps([{
        "intent": i.get("intent"),
        "outcome": i.get("outcome"),
        "escalated": i.get("escalated"),
        "user_message": (i.get("user_message") or "")[:100],
        "sentiment": i.get("sentiment")
    } for i in interactions[:30]])
    
    # Get objections
    r2 = requests.get(
        f"{SUPABASE_URL}/rest/v1/memories",
        headers=HEADERS,
        params={"memory_type": "eq.objection", "limit": 10}
    )
    objections = [o.get("value", "")[:50] for o in (r2.json() if r2.status_code == 200 else [])]
    
    # AI Analysis
    prompt = f"""You are the Playbook Optimizer for AI Service Co.
    
Analyze these {len(interactions)} recent sales interactions:
{batch}

Recent objections logged: {objections}

Your task:
1. Identify the TOP 3 script improvements that would increase booking rate
2. Identify 1 knowledge base gap (question that couldn't be answered)
3. Rate each change as low/med/high risk

Rules:
- Do NOT suggest changes to pricing, guarantees, or compliance rules
- Focus on wording, timing, and objection handling
- Be specific and actionable

Return ONLY valid JSON:
{{
  "script_updates": [
    {{"where": "sms_opening|pricing_response|booking_cta|objection_handling", "change": "...", "risk": "low|med|high", "expected_impact": "..."}}
  ],
  "kb_gap": {{"question": "...", "recommended_answer": "..."}},
  "summary": "1-2 sentence summary of findings"
}}"""

    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60
    )
    
    if r.status_code != 200:
        print(f"[ERROR] Gemini failed: {r.status_code}")
        return {"error": "AI analysis failed"}
    
    try:
        result_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        # Clean markdown if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        analysis = json.loads(result_text)
        print(f"[ANALYSIS] {analysis.get('summary', 'No summary')}")
        
        # Save to playbook_updates
        for update in analysis.get("script_updates", []):
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/playbook_updates",
                headers=HEADERS,
                json={
                    "update_type": "script_change",
                    "where_applies": update.get("where"),
                    "change_description": update.get("change"),
                    "risk_level": update.get("risk"),
                    "reason": update.get("expected_impact"),
                    "status": "proposed"  # NEVER auto-apply
                }
            )
            print(f"  [SAVED] {update.get('where')}: {update.get('risk')} risk")
        
        # Save KB gap
        kb_gap = analysis.get("kb_gap", {})
        if kb_gap.get("question"):
            requests.post(
                f"{SUPABASE_URL}/rest/v1/playbook_updates",
                headers=HEADERS,
                json={
                    "update_type": "kb_gap",
                    "change_description": kb_gap.get("question"),
                    "reason": kb_gap.get("recommended_answer"),
                    "risk_level": "low",
                    "status": "proposed"
                }
            )
            print(f"  [KB GAP] {kb_gap.get('question')[:50]}...")
        
        return {
            "status": "success",
            "updates_saved": len(analysis.get("script_updates", [])),
            "kb_gaps": 1 if kb_gap.get("question") else 0,
            "summary": analysis.get("summary")
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to parse: {e}")
        return {"error": str(e)}


@app.local_entrypoint()
def main():
    result = run_nightly_optimizer.remote()
    print(f"\nResult: {result}")


if __name__ == "__main__":
    print("Deploy with: modal deploy modal_playbook_optimizer.py")
    print("Will run at 3am daily (UTC)")
