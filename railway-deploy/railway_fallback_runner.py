"""
AGENT: Railway Fallback Runner
Always-on fallback for webhook processing, campaign scheduler, dispatcher.
Returns structured JSON only.
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

app = FastAPI(title="Empire Fallback Runner", docs_url=None, redoc_url=None)

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo")
PORT = int(os.getenv("PORT", "8080"))
TZ = ZoneInfo("America/New_York")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def is_business_hours() -> bool:
    now = datetime.now(TZ)
    return 8 <= now.hour < 17 and now.weekday() < 5

async def log_to_supabase(table: str, data: dict):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=5
            )
    except:
        pass

@app.get("/health")
async def health():
    ts = now_iso()
    asyncio.create_task(log_to_supabase("health_logs", {
        "timestamp": ts,
        "component": "fallback_runner",
        "status": "ok",
        "action_taken": "health_check",
        "message": ""
    }))
    return JSONResponse({"status": "ok", "timestamp": ts})

@app.post("/webhook")
async def webhook(request: Request):
    ts = now_iso()
    try:
        payload = await request.json()
    except:
        return JSONResponse({"timestamp": ts, "status": "error", "error": "invalid_json"}, status_code=400)
    
    event_type = payload.get("type") or payload.get("event") or "unknown"
    contact_id = payload.get("contactId") or payload.get("contact_id") or ""
    
    # Log webhook receipt
    asyncio.create_task(log_to_supabase("webhook_logs", {
        "timestamp": ts,
        "source": request.headers.get("User-Agent", "unknown"),
        "payload": payload,
        "forwarded_to": "fallback_dispatcher",
        "result_status": 200
    }))
    
    # Dispatch logic placeholder
    # TODO: Route to Sarah/Christina based on event_type
    
    return JSONResponse({
        "timestamp": ts,
        "status": "ok",
        "event_type": event_type,
        "contact_id": contact_id
    })

async def campaign_scheduler():
    """Background scheduler - runs every 5 minutes during business hours"""
    while True:
        ts = now_iso()
        if is_business_hours():
            # Log campaign check
            await log_to_supabase("campaign_logs", {
                "timestamp": ts,
                "lead_id": None,
                "touch_type": "scheduler_check",
                "disposition": "pending",
                "error": None
            })
            # TODO: Fetch pending touches from Supabase and execute
        await asyncio.sleep(300)

@app.on_event("startup")
async def startup():
    ts = now_iso()
    await log_to_supabase("health_logs", {
        "timestamp": ts,
        "component": "fallback_runner",
        "status": "started",
        "action_taken": "startup",
        "message": f"Port {PORT}"
    })
    asyncio.create_task(campaign_scheduler())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
