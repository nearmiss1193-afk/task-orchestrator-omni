"""
CLOUD INSPECTOR (Phase 9: The Panopticon)
=========================================
Hourly health patrol of all Empire systems.
Checks endpoints, webhooks, landing pages, and reports to Super Brain.
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Systems to monitor
ENDPOINTS = [
    # Modal Webhooks
    {"name": "Vapi Webhook", "url": "https://nearmiss1193-afk--health-live.modal.run", "type": "webhook"},
    
    # Landing Pages
    {"name": "Main Site", "url": "https://aiserviceco.com", "type": "website"},
    {"name": "HVAC Landing", "url": "https://aiserviceco.com/hvac.html", "type": "landing"},
    {"name": "Plumbing Landing", "url": "https://aiserviceco.com/plumbing.html", "type": "landing"},
    {"name": "Roofing Landing", "url": "https://aiserviceco.com/roofing.html", "type": "landing"},
    
    # Internal APIs
    {"name": "Supabase Health", "url": f"{SUPABASE_URL}/rest/v1/", "type": "api", "headers": {"apikey": SUPABASE_KEY or ""}},
]

def log_to_superbrain(level, message, metadata=None):
    """Log events to system_logs table."""
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            client.table('system_logs').insert({
                'level': level,
                'message': message,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat()
            }).execute()
    except Exception as e:
        print(f"Log error: {e}")

def check_endpoint(endpoint):
    """Check a single endpoint and return status."""
    result = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "type": endpoint["type"],
        "status": "UNKNOWN",
        "response_time_ms": None,
        "error": None
    }
    
    try:
        headers = endpoint.get("headers", {})
        start = datetime.now()
        response = requests.get(endpoint["url"], headers=headers, timeout=10)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        result["response_time_ms"] = round(elapsed, 2)
        
        if response.status_code == 200:
            result["status"] = "HEALTHY"
        elif response.status_code < 500:
            result["status"] = "DEGRADED"
            result["error"] = f"HTTP {response.status_code}"
        else:
            result["status"] = "DOWN"
            result["error"] = f"HTTP {response.status_code}"
            
    except requests.Timeout:
        result["status"] = "TIMEOUT"
        result["error"] = "Request timed out (10s)"
    except requests.ConnectionError as e:
        result["status"] = "UNREACHABLE"
        result["error"] = str(e)[:100]
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)[:100]
    
    return result

def run_patrol():
    """Run full system patrol."""
    print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] PANOPTICON PATROL INITIATED")
    print("=" * 50)
    
    results = []
    healthy = 0
    issues = 0
    
    for endpoint in ENDPOINTS:
        result = check_endpoint(endpoint)
        results.append(result)
        
        icon = "✅" if result["status"] == "HEALTHY" else "⚠️" if result["status"] == "DEGRADED" else "❌"
        time_str = f"{result['response_time_ms']}ms" if result['response_time_ms'] else "N/A"
        
        print(f"  {icon} {result['name']}: {result['status']} ({time_str})")
        
        if result["status"] == "HEALTHY":
            healthy += 1
        else:
            issues += 1
            if result["error"]:
                print(f"      └─ {result['error']}")
    
    print("=" * 50)
    
    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_checks": len(results),
        "healthy": healthy,
        "issues": issues,
        "results": results
    }
    
    # Log to Super Brain
    if issues > 0:
        log_to_superbrain('WARNING', f'Panopticon: {issues}/{len(results)} systems have issues', summary)
        print(f"⚠️  ALERT: {issues} system(s) require attention!")
    else:
        log_to_superbrain('INFO', f'Panopticon: All {healthy} systems healthy', summary)
        print(f"✅ All {healthy} systems operational.")
    
    return summary

if __name__ == "__main__":
    run_patrol()
