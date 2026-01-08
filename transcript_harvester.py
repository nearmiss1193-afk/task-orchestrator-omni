"""
ENHANCED TRANSCRIPT HARVESTER WITH GROK ANALYSIS
================================================
Fetches Vapi transcripts, stores in Supabase, and uses Grok for deep analysis.
This is the SOP script for continuous agent learning.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Import Grok client for analysis
try:
    from modules.grok_client import GrokClient, grok_analyze_call_transcript
    GROK_AVAILABLE = True
except ImportError:
    GROK_AVAILABLE = False

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"


def ensure_table_exists():
    """Try to create table if it doesn't exist by attempting an insert"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Check if table exists with a simple query
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/call_transcripts?limit=1",
        headers=headers,
        timeout=10
    )
    
    if res.status_code == 200:
        return True
    
    # Table doesn't exist - try creating via insert (will fail but that's ok)
    print("⚠️ call_transcripts table not found. Create it in Supabase SQL Editor:")
    print("   https://supabase.com/dashboard/project/rzcpfwkygdvoshtwxncs/sql/new")
    return False


def fetch_vapi_calls(limit=50):
    """Fetch recent calls from Vapi API"""
    headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}
    res = requests.get(f"https://api.vapi.ai/call?limit={limit}", headers=headers, timeout=30)
    return res.json() if res.status_code == 200 else []


def fetch_call_detail(call_id):
    """Fetch full call details including transcript"""
    headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}
    res = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=headers, timeout=30)
    return res.json() if res.status_code == 200 else None


def store_transcript(call_data, grok_analysis=None):
    """Store call transcript in Supabase with optional Grok analysis"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    payload = {
        "call_id": call_data.get("id"),
        "assistant_id": call_data.get("assistantId"),
        "assistant_name": call_data.get("assistant", {}).get("name", "Unknown"),
        "customer_phone": call_data.get("customer", {}).get("number"),
        "customer_name": call_data.get("customer", {}).get("name"),
        "status": call_data.get("status"),
        "duration_seconds": call_data.get("durationSeconds"),
        "transcript": call_data.get("transcript"),
        "summary": call_data.get("summary"),
        "analysis": json.dumps(call_data.get("analysis", {})),
        "structured_data": json.dumps(call_data.get("structuredData", {})),
        "success_evaluation": call_data.get("successEvaluation"),
        "cost": call_data.get("cost"),
        "started_at": call_data.get("startedAt"),
        "ended_at": call_data.get("endedAt"),
        "created_at": call_data.get("createdAt"),
        "metadata": json.dumps(call_data)
    }
    
    # Add Grok analysis if available
    if grok_analysis:
        payload["grok_analysis"] = json.dumps(grok_analysis)
        payload["learnings_extracted"] = True
    
    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/call_transcripts",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    return res.status_code in [200, 201, 409]  # 409 = duplicate, that's ok


def extract_learnings(calls_data):
    """Extract actionable learnings from call data"""
    learnings = {
        "total_calls": len(calls_data),
        "successful_calls": 0,
        "total_duration_minutes": 0,
        "objections_encountered": [],
        "conversion_patterns": [],
        "improvement_suggestions": [],
        "generated_at": datetime.now().isoformat()
    }
    
    for call in calls_data:
        # Duration
        duration = call.get("durationSeconds", 0) or 0
        learnings["total_duration_minutes"] += duration / 60
        
        # Success tracking
        if call.get("analysis", {}).get("outcome") == "booked":
            learnings["successful_calls"] += 1
        
        # Extract objections
        structured = call.get("structuredData", {})
        if structured and isinstance(structured, dict):
            objections = structured.get("objections", [])
            if objections:
                learnings["objections_encountered"].extend(objections)
    
    # Dedupe
    learnings["objections_encountered"] = list(set(learnings["objections_encountered"]))
    learnings["total_duration_minutes"] = round(learnings["total_duration_minutes"], 1)
    
    return learnings


def run_full_harvest(with_grok=True):
    """Main harvest function with optional Grok analysis"""
    print("🚀 CALL TRANSCRIPT HARVESTER (ENHANCED)")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 60)
    
    # Check table
    table_ready = ensure_table_exists()
    
    # Check Grok
    grok_client = None
    if with_grok and GROK_AVAILABLE:
        grok_client = GrokClient()
        if grok_client.api_key:
            print("🧠 Grok analysis: ENABLED")
        else:
            print("🧠 Grok analysis: DISABLED (no API key)")
            grok_client = None
    
    # Fetch calls
    print("\n📞 Fetching calls from Vapi...")
    calls = fetch_vapi_calls(limit=100)
    print(f"✅ Retrieved {len(calls)} calls")
    
    if not calls:
        print("No calls to process.")
        return
    
    # Process each call
    stored = 0
    analyzed = 0
    
    for call in calls:
        call_id = call.get("id")
        detail = fetch_call_detail(call_id)
        
        if not detail:
            continue
        
        transcript = detail.get("transcript")
        
        # Grok analysis for calls with transcripts
        grok_analysis = None
        if grok_client and transcript and len(transcript) > 100:
            try:
                grok_analysis = grok_analyze_call_transcript(transcript, grok_client)
                analyzed += 1
            except Exception as e:
                print(f"  ⚠️ Grok analysis failed: {e}")
        
        # Store
        if table_ready and store_transcript(detail, grok_analysis):
            stored += 1
    
    print("-" * 60)
    print(f"📊 HARVEST COMPLETE")
    print(f"   Stored: {stored}")
    print(f"   Analyzed with Grok: {analyzed}")
    
    # Extract and save learnings
    learnings = extract_learnings(calls)
    
    with open("agent_learnings.json", "w") as f:
        json.dump(learnings, f, indent=2)
    
    print(f"\n🧠 LEARNINGS:")
    print(f"   Total Calls: {learnings['total_calls']}")
    print(f"   Successful: {learnings['successful_calls']}")
    print(f"   Total Time: {learnings['total_duration_minutes']} minutes")
    print(f"   Objections Found: {len(learnings['objections_encountered'])}")
    
    print("\n✅ Saved to agent_learnings.json")
    
    return learnings


if __name__ == "__main__":
    run_full_harvest()
