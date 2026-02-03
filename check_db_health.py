
import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
from modules.database.supabase_client import get_supabase
from datetime import datetime, timedelta

def check_system_health():
    supabase = get_supabase()
    if not supabase:
        return

    results = {}
    
    try:
        logs = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(20).execute()
        results["brain_logs"] = logs.data
    except Exception as e:
        results["brain_logs_error"] = str(e)

    try:
        errors = supabase.table("error_logs").select("*").order("created_at", desc=True).limit(20).execute()
        results["error_logs"] = errors.data
    except Exception as e:
        results["error_logs_error"] = str(e)

    try:
        touches = supabase.table("outbound_touches").select("*").order("ts", desc=True).limit(20).execute()
        results["outbound_touches"] = touches.data
    except Exception as e:
        results["outbound_touches_error"] = str(e)

    with open("db_health_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    check_system_health()
