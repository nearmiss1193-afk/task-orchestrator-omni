"""
WEEKLY DIGEST WRAPPER — Phase 14
Handles weekly newsletter distribution and edition rotation.
"""
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, '.')

from modules.database.supabase_client import get_supabase
from workers.newsletter import send_newsletter

def run_weekly_digest(dry_run=False):
    supabase = get_supabase()
    if not supabase:
        print("❌ Error: Could not connect to Supabase.")
        return

    # 1. Get current edition from system_state
    try:
        res = supabase.table("system_state").select("last_error").eq("key", "newsletter_edition").execute()
        if res.data and res.data[0].get("last_error"):
            current_edition = int(res.data[0]["last_error"])
        else:
            current_edition = 0
            # Init if not exists
            supabase.table("system_state").upsert({
                "key": "newsletter_edition", 
                "status": "working",
                "last_error": "0"
            }, on_conflict="key").execute()
    except Exception as e:
        print(f"⚠️ Failed to fetch newsletter_edition, defaulting to 0: {e}")
        current_edition = 0

    print(f"📧 Starting Newsletter Run: Edition {current_edition}")
    
    # 2. Send Newsletter
    try:
        # Pass dry_run. workers/newsletter.py handles Resend API calls.
        newsletter = send_newsletter(supabase, edition=current_edition, dry_run=dry_run)
        
        if not dry_run:
            # 3. Increment edition for next week
            next_edition = current_edition + 1
            supabase.table("system_state").upsert({
                "key": "newsletter_edition",
                "status": "working",
                "last_error": str(next_edition)
            }, on_conflict="key").execute()
            print(f"✅ Newsletter Edition {current_edition} sent. Next edition: {next_edition}")
        else:
            print(f"⚠️ Dry run complete for Edition {current_edition}.")
            
    except Exception as e:
        print(f"❌ Newsletter Run Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check for dry-run flag
    dry_run_arg = any(arg in sys.argv for arg in ["--dry-run", "--dryrun", "-d"])
    run_weekly_digest(dry_run=dry_run_arg)
