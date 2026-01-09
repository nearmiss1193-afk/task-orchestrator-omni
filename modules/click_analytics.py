"""
CLICK ANALYTICS TRACKER
=======================
Tracks CTA click-through rates and surfaces failures.
Integrates with Supabase to store click events and detect silent 404 patterns.

Usage:
    from modules.click_analytics import log_click, get_cta_performance
    
    # Log a click event (called from redirect handler)
    log_click(campaign_id, cta_type, url, success=True)
    
    # Get performance report
    report = get_cta_performance(days=7)
"""
import os
from datetime import datetime, timedelta
from supabase import create_client

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")


def get_client():
    """Get Supabase client."""
    key = SUPABASE_KEY or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1OTA0MjQsImV4cCI6MjA4MjE2NjQyNH0.dluuiK-jr-3Z_oksYHS4saSthpkppLHQGnl6YtploPU"
    return create_client(SUPABASE_URL, key)


def log_click(campaign_id: str, cta_type: str, target_url: str, 
              success: bool = True, status_code: int = None,
              source: str = "email") -> bool:
    """
    Log a CTA click event to the database.
    
    Args:
        campaign_id: Identifier for the campaign (e.g., "hvac_tampa_20260109")
        cta_type: Type of CTA (e.g., "book_demo", "see_features", "call_now")
        target_url: The destination URL
        success: Whether the click resolved successfully
        status_code: HTTP status code if available
        source: Where the click came from (email, sms, landing_page)
    """
    try:
        client = get_client()
        
        event = {
            "campaign_id": campaign_id,
            "cta_type": cta_type,
            "target_url": target_url,
            "success": success,
            "status_code": status_code,
            "source": source,
            "created_at": datetime.utcnow().isoformat()
        }
        
        client.table("click_events").insert(event).execute()
        return True
        
    except Exception as e:
        print(f"[ANALYTICS] Failed to log click: {e}")
        return False


def get_cta_performance(days: int = 7, campaign_id: str = None) -> dict:
    """
    Get CTA performance report.
    
    Returns aggregated stats on click success/failure rates.
    """
    try:
        client = get_client()
        
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        query = client.table("click_events").select("*").gte("created_at", since)
        
        if campaign_id:
            query = query.eq("campaign_id", campaign_id)
        
        result = query.execute()
        events = result.data
        
        if not events:
            return {"total_clicks": 0, "success_rate": 0, "failures": []}
        
        total = len(events)
        successes = sum(1 for e in events if e.get("success"))
        failures = [e for e in events if not e.get("success")]
        
        # Group failures by URL
        failure_urls = {}
        for f in failures:
            url = f.get("target_url", "unknown")
            failure_urls[url] = failure_urls.get(url, 0) + 1
        
        return {
            "total_clicks": total,
            "success_rate": round(successes / total * 100, 1) if total else 0,
            "failures": failures,
            "failure_count": len(failures),
            "failure_urls": failure_urls,
            "by_cta_type": _group_by_cta_type(events)
        }
        
    except Exception as e:
        print(f"[ANALYTICS] Failed to get performance: {e}")
        return {"error": str(e)}


def _group_by_cta_type(events: list) -> dict:
    """Group click events by CTA type."""
    groups = {}
    for e in events:
        cta = e.get("cta_type", "unknown")
        if cta not in groups:
            groups[cta] = {"total": 0, "success": 0}
        groups[cta]["total"] += 1
        if e.get("success"):
            groups[cta]["success"] += 1
    
    # Calculate rates
    for cta in groups:
        total = groups[cta]["total"]
        success = groups[cta]["success"]
        groups[cta]["success_rate"] = round(success / total * 100, 1) if total else 0
    
    return groups


def print_performance_report(days: int = 7):
    """Print a human-readable performance report."""
    report = get_cta_performance(days)
    
    print("=" * 60)
    print(f"CTA CLICK ANALYTICS - Last {days} Days")
    print("=" * 60)
    
    if "error" in report:
        print(f"Error: {report['error']}")
        return
    
    print(f"\nTotal Clicks: {report['total_clicks']}")
    print(f"Success Rate: {report['success_rate']}%")
    print(f"Failures: {report['failure_count']}")
    
    if report.get("failure_urls"):
        print("\nFailing URLs:")
        for url, count in sorted(report["failure_urls"].items(), key=lambda x: -x[1]):
            print(f"  [{count}x] {url}")
    
    if report.get("by_cta_type"):
        print("\nBy CTA Type:")
        for cta, stats in report["by_cta_type"].items():
            print(f"  {cta}: {stats['success']}/{stats['total']} ({stats['success_rate']}%)")
    
    print("=" * 60)


# SQL to create the click_events table (run in Supabase SQL editor)
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS click_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id TEXT,
    cta_type TEXT,
    target_url TEXT,
    success BOOLEAN DEFAULT true,
    status_code INTEGER,
    source TEXT DEFAULT 'email',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance queries
CREATE INDEX IF NOT EXISTS idx_click_events_created_at ON click_events(created_at);
CREATE INDEX IF NOT EXISTS idx_click_events_campaign ON click_events(campaign_id);

-- Disable RLS for simplicity (enable if needed)
ALTER TABLE click_events DISABLE ROW LEVEL SECURITY;
"""


if __name__ == "__main__":
    print("Click Analytics Module")
    print("Run print_performance_report() to see stats")
    print("\nTo set up the database table, run this SQL in Supabase:")
    print(CREATE_TABLE_SQL)
