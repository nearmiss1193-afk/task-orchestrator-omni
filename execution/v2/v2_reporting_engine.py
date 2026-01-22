import modal
import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

# Define the image
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "pandas") # Pandas for easy data aggregation
)

# Modal App Definition - Conditional
IF_MODAL = os.environ.get("MODAL_RUNTIME") or ("modal" in sys.modules and __name__ != "__main__")

if IF_MODAL:
    app = modal.App("v2-automated-reporting")
    VAULT = modal.Secret.from_name("agency-vault")

    @app.function(
        image=image, 
        secrets=[VAULT], 
        # Schedule: Daily at 6 PM EST (23:00 UTC)
        schedule=modal.Cron("0 23 * * *")
    )
    async def generate_daily_report():
        return await run_reporting_engine()
else:
    app = None
    async def generate_daily_report():
        return await run_reporting_engine()


async def run_reporting_engine():
    """
    Core logic: Queries DB and generates Markdown report.
    """
    print(f"📊 [REPORTING] Generating Daily Situation Report...")
    
    from supabase import create_client
    
    # Setup Clients
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ [REPORTING] Supabase credentials missing.")
        return {"error": "Missing Supabase creds"}

    supabase = create_client(supabase_url, supabase_key)

    # 1. Fetch Contact Stats
    try:
        # Total Contacts
        res_total = supabase.table("contacts_master").select("*", count="exact", head=True).execute()
        total_contacts = res_total.count

        # New leads (last 24h)
        yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        res_new = supabase.table("contacts_master").select("*", count="exact", head=True).filter("created_at", "gt", yesterday).execute()
        new_contacts = res_new.count

        # Avg Score (Need to fetch data for this, no avg aggregate in simple API usually without RPC)
        # We'll fetch just scores to minimize bandwidth
        res_scores = supabase.table("contacts_master").select("lead_score").execute()
        scores = [r['lead_score'] for r in res_scores.data if r['lead_score'] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Status Breakdown
        res_status = supabase.table("contacts_master").select("status").execute()
        status_counts = {}
        for r in res_status.data:
            s = r.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

    except Exception as e:
        print(f"⚠️ [REPORTING] Failed to fetch contact stats: {e}")
        total_contacts = 0
        new_contacts = 0
        avg_score = 0
        status_counts = {}

    # 2. Fetch System Health
    try:
        res_health = supabase.table("system_health").select("*").execute()
        health_data = res_health.data
    except Exception as e:
        print(f"⚠️ [REPORTING] Failed to fetch system health: {e}")
        health_data = []

    # 3. Generate Markdown
    report_date = datetime.now().strftime("%Y-%m-%d")
    markdown_report = f"""
# 🏁 Empire Daily Situation Report - {report_date}

## ⚡ Quick Stats
- **Total Leads**: {total_contacts}
- **New Leads (24h)**: {new_contacts}
- **Avg Lead Score**: {avg_score:.1f}

## 📊 Pipeline Status
"""
    for status, count in status_counts.items():
        markdown_report += f"- **{status.title()}**: {count}\n"

    markdown_report += "\n## 🏥 System Health\n"
    if health_data:
        for component in health_data:
            name = component.get("component_name", "Unknown")
            status = component.get("status", "Unknown")
            last_checked = component.get("last_checked", "")
            icon = "✅" if status == "healthy" else "⚠️"
            markdown_report += f"- {icon} **{name}**: {status} (Checked: {last_checked})\n"
    else:
        markdown_report += "- *No health data available.*\n"

    print("\n" + "="*40)
    print(markdown_report)
    print("="*40 + "\n")

    return {
        "status": "success",
        "report_length": len(markdown_report),
        "metrics": {
            "total": total_contacts,
            "new": new_contacts,
            "avg_score": avg_score
        }
    }


# Local test hook
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    # Load local env for testing
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.local")
    except: 
        pass
    
    # Run async test
    async def main():
        print("🧪 [TEST] Running Reporting Engine Locally...")
        await run_reporting_engine()
    
    asyncio.run(main())
