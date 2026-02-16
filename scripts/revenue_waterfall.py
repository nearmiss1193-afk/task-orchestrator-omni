"""
REVENUE WATERFALL DIAGNOSTIC v6.0
=================================
Empirical verification of the income pipeline.
"""
import os
import json
from datetime import datetime, timezone, timedelta
from modules.database.supabase_client import get_supabase

def run_waterfall():
    supabase = get_supabase()
    now = datetime.now(timezone.utc)
    day_ago = (now - timedelta(days=1)).isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    
    print(f"\n--- INCOME PIPELINE CHECK [{now.strftime('%Y-%m-%d')}] ---")
    
    # Step 1: SENDING?
    sending = supabase.table("outbound_touches").select("id", count="exact").gte("ts", day_ago).execute()
    print(f"Step 1: SENDING?    → {sending.count or 0} emails in last 24h")
    
    # Step 2: OPENING?
    # Note: Using the human_intent filter from Phase 6
    opening = supabase.table("outbound_touches").select("id", count="exact").eq("payload->>opened", "true").gte("ts", week_ago).execute()
    print(f"Step 2: OPENING?    → {opening.count or 0} human opens in last 7d")
    
    # Step 3: REPLYING?
    replying = supabase.table("outbound_touches").select("id", count="exact").eq("status", "replied").gte("ts", week_ago).execute()
    print(f"Step 3: REPLYING?   → {replying.count or 0} replies in last 7d")
    
    # Step 4: BOOKING?
    # Checking for status changes to 'appointment' or similar in contacts_master
    booking = supabase.table("contacts_master").select("id", count="exact").eq("status", "appointment").execute()
    print(f"Step 4: BOOKING?    → {booking.count or 0} appointments booked")
    
    # Step 5: PAYING?
    paying = supabase.table("contacts_master").select("id", count="exact").eq("status", "customer").execute()
    print(f"Step 5: PAYING?     → {paying.count or 0} payments/customers total")
    
    # Step 6: PIPELINE?
    pipeline = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
    print(f"Step 6: PIPELINE?   → {pipeline.count or 0} contactable leads remain")
    
    # SOURCE BREAKDOWN
    print("\n--- SOURCE BREAKDOWN ---")
    sources = supabase.table("contacts_master").select("source").execute()
    s_map = {}
    for r in sources.data:
        s = r.get("source", "unknown")
        s_map[s] = s_map.get(s, 0) + 1
    summary = (
        f"--- INCOME PIPELINE CHECK [{now.strftime('%Y-%m-%d')}] ---\n"
        f"Step 1: SENDING?    → {sending.count or 0} emails in last 24h\n"
        f"Step 2: OPENING?    → {opening.count or 0} human opens in last 7d\n"
        f"Step 3: REPLYING?   → {replying.count or 0} replies in last 7d\n"
        f"Step 4: BOOKING?    → {booking.count or 0} appointments booked\n"
        f"Step 5: PAYING?     → {paying.count or 0} payments/customers total\n"
        f"Step 6: PIPELINE?   → {pipeline.count or 0} contactable leads remain\n"
        f"\n--- SOURCE BREAKDOWN ---\n"
    )
    for s, c in sorted(s_map.items(), key=lambda x: x[1], reverse=True):
        summary += f" - {s}: {c} leads\n"
        
    return summary

if __name__ == "__main__":
    rep = run_waterfall()
    print(rep)
