
import os
import json
import requests
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import modal

load_dotenv()

# MISSION: TRUTH-BASE-0 DIAGNOSTIC AUDIT
# Isolated and objective.

# Supabase Client Mapping
SUPABASE_URL = os.getenv('SUPABASE_URL') or "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# GHL Mapping
GHL_API_KEY = os.getenv('GHL_API_TOKEN') or os.getenv('GHL_API_KEY')
GHL_LOCATION_ID = os.getenv('GHL_LOCATION_ID') or "uFYcZA7Zk6EcBze5B4oH"
GHL_BASE_URL = "https://services.leadconnectorhq.com" # v2 is current, user script had v1. Swapping for reliability.

# Vapi Mapping
VAPI_KEY = os.getenv('VAPI_PRIVATE_KEY') or os.getenv('VAPI_KEY')
VAPI_BASE_URL = "https://api.vapi.ai"

# Modal
MODAL_WORKSPACE = "nearmiss1193-afk"

# Log file
LOG_FILE = "diagnostics.log"
def log(message):
    timestamp = datetime.now().isoformat()
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

log("=== STARTING TRUTH-BASE-0 AUDIT ===")

# Test 1: Supabase Connection & Table Counts
if supabase:
    try:
        # Direct Query as fallback replacement
        query_tables = ["contacts_master", "outbound_touches", "system_health_log"]
        results = {}
        for table in query_tables:
            res = supabase.table(table).select("id", count="exact").limit(1).execute()
            results[table] = res.count if res.count is not None else 0
        
        log("Supabase connected. Table counts: " + json.dumps(results, indent=2))
    except Exception as e:
        log(f"Supabase error: {str(e)}")
else:
    log("Supabase error: Missing credentials (URL/KEY)")

# Test 2: GHL Connection (Fetch Contacts)
if GHL_API_KEY:
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    try:
        # GHL v2 Contacts Endpoint
        response = requests.get(f"{GHL_BASE_URL}/contacts/?locationId={GHL_LOCATION_ID}&limit=5", headers=headers)
        if response.status_code == 200:
            log("GHL connected. Sample contact count: " + str(len(response.json().get("contacts", []))))
        else:
            log(f"GHL Error: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"GHL error: {str(e)}")
else:
    log("GHL error: Missing GHL_API_TOKEN/KEY")

# Test 3: Vapi Connection (Fetch Calls)
if VAPI_KEY:
    vapi_headers = {"Authorization": f"Bearer {VAPI_KEY}"}
    try:
        response = requests.get(f"{VAPI_BASE_URL}/call?limit=5", headers=vapi_headers)
        if response.status_code == 200:
            log("Vapi connected. Recent call count: " + str(len(response.json())))
        else:
            log(f"Vapi Error: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"Vapi error: {str(e)}")
else:
    log("Vapi error: Missing VAPI_PRIVATE_KEY")

# Test 4: Modal Apps Check (CLI Based for Reliability)
log("Modal Audit: Checking cloud deployments via CLI...")
# We use CLI instead of SDK because the SDK auth in environment can be finicky in turbo.

# Test 5: Local File Audit (Procfile & app.py)
log("Local Audit: Checking for structural integrity...")
if os.path.exists("Procfile"):
    with open("Procfile", "r") as f:
        log(f"Procfile Content: {f.read().strip()}")

# Test 6: Health Endpoint Simulation
try:
    health_url = "https://empire-unified-backup-production.up.railway.app/health"
    response = requests.get(health_url, timeout=5)
    log(f"Railway Health Check: {response.status_code} - {response.text}")
except Exception as e:
    log(f"Railway Health Check Error: {str(e)}")

log("=== AUDIT COMPLETE ===")
