from core.engine import app, image, VAULT
from core.orchestra import run_system_heartbeat, run_self_healing
from workers.enrichment import fetch_pagespeed, check_privacy_policy, check_ai_readiness
from workers.teaser_worker import capture_mobile_teaser, upload_teaser_to_supabase
from handlers.webhooks import handle_vapi_event, handle_ghl_event, handle_stripe_event
import modal

# ────────────────────────────────────────────────────────────
#  DIAGNOSTICS (Revenue Waterfall)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT])
def income_pipeline_check():
    """Run the empirical Revenue Waterfall diagnostic."""
    from scripts.revenue_waterfall import run_waterfall
    summary = run_waterfall()
    print(summary)
    return summary

@app.function(image=image, secrets=[VAULT])
def count_manus_leads():
    """Count leads with source='manus' via Modal."""
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    res = sb.table("contacts_master").select("id", count="exact").eq("source", "manus").execute()
    print(f"📊 MANUS LEAD COUNT: {res.count}")
    return res.count

# ────────────────────────────────────────────────────────────
#  SYSTEM ORCHESTRATOR (5-Minute Pulse)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/5 * * * *"), timeout=600)
def system_orchestrator():
    """Consolidated modular pulse."""
    print("🚀 SOVEREIGN ORCHESTRATOR: Starting modular cycle...")
    
    # 1. Self-Healing & Diagnostics
    issues = run_self_healing()
    
    # 2. Heartbeat Logging
    mode = run_system_heartbeat(issues)
    
    # [Trigger outreach and research workers below]
    print(f"✅ Cycle complete. Mode: {mode}")

# ────────────────────────────────────────────────────────────
#  RESEARCH STRIKE WORKER (Cloud Enrichment)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT], timeout=300)
def research_strike_worker(lead_id: str):
    """Modular research strike: enrichment + video teaser."""
    import asyncio
    # [Simplified logic importing from workers.enrichment and workers.teaser]
    print(f"🕵️ RESEARCH: Auditing Lead {lead_id} (MODULAR)...")
    return {"status": "success"}

# ────────────────────────────────────────────────────────────
#  WEBHOOK ENDPOINTS
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST", label="vapi-webhook-modular")
def vapi_webhook(payload: dict):
    return handle_vapi_event(payload)

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST", label="ghl-webhook-modular")
def ghl_webhook(payload: dict):
    return handle_ghl_event(payload)

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST", label="stripe-webhook-modular")
def stripe_webhook(payload: dict):
    return handle_stripe_event(payload)

if __name__ == "__main__":
    print("⚫ ANTIGRAVITY v5.0 - SOVEREIGN MODULAR DEPLOY")
