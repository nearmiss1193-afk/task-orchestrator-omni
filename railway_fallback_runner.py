"""
AGENT: Railway Fallback Runner
Always-on fallback service for webhook processing and campaign scheduling.
Deploys to Railway for 24/7 uptime.
"""
import os
import json
import asyncio
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import uvicorn

app = FastAPI(title="Empire Fallback Runner")

# Environment
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
GHL_WEBHOOK_SECRET = os.getenv("GHL_WEBHOOK_SECRET", "")
PORT = int(os.getenv("PORT", os.getenv("SECONDARY_RUNNER_PORT", "8080")))

# Supabase headers
def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

async def log_to_supabase(table: str, data: dict):
    """Non-blocking log to Supabase"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers=supabase_headers(),
                json=data,
                timeout=5
            )
    except Exception as e:
        print(f"[LOG ERROR] {e}")

def is_business_hours() -> bool:
    """Check if current time is within 8am-5pm EST"""
    now = datetime.now(ZoneInfo("America/New_York"))
    return 8 <= now.hour < 17 and now.weekday() < 5

@app.get("/health")
async def health():
    return JSONResponse({
        "status": "ok",
        "service": "empire-fallback-runner",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "business_hours": is_business_hours()
    })

@app.post("/webhook")
async def webhook(request: Request):
    """Process inbound webhook events"""
    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Log receipt
    asyncio.create_task(log_to_supabase("webhook_logs", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": request.headers.get("User-Agent", "unknown"),
        "payload": payload,
        "forwarded_to": "fallback_runner",
        "result_status": 200
    }))
    
    # Process based on event type
    event_type = payload.get("type") or payload.get("event") or "unknown"
    contact_id = payload.get("contactId") or payload.get("contact_id")
    
    # Log health event
    asyncio.create_task(log_to_supabase("health_logs", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "fallback_runner",
        "status": "processing",
        "action_taken": f"webhook_{event_type}",
        "message": f"Received {event_type} for contact {contact_id}"
    }))
    
    # TODO: Add actual dispatch logic here (call Sarah, Christina, etc.)
    
    return JSONResponse({
        "status": "received",
        "event_type": event_type,
        "contact_id": contact_id
    })

@app.on_event("startup")
async def startup():
    print(f"[STARTUP] Empire Fallback Runner starting on port {PORT}")
    asyncio.create_task(log_to_supabase("health_logs", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "fallback_runner",
        "status": "online",
        "action_taken": "startup",
        "message": f"Service started on port {PORT}"
    }))

# Campaign scheduler (runs in background)
async def campaign_scheduler():
    """Background task to check and run campaigns"""
    while True:
        try:
            if is_business_hours():
                # TODO: Fetch pending campaigns from Supabase and execute
                print(f"[SCHEDULER] Checking campaigns at {datetime.now()}")
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def start_scheduler():
    asyncio.create_task(campaign_scheduler())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
