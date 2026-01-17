"""
Railway Fallback Runner - FastAPI service for webhook handling when Modal is unavailable
"""
from fastapi import FastAPI, Request
from datetime import datetime, timezone
import os
import httpx

app = FastAPI(title="Empire Fallback Runner", version="1.0")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "railway-fallback-runner",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhooks when primary Modal orchestrator is down"""
    try:
        payload = await request.json()
    except:
        payload = {"raw": await request.body()}
    
    # Log to Supabase
    await log_to_supabase("webhook_received", payload)
    
    # Process webhook (basic acknowledgment for now)
    return {
        "status": "ok",
        "handler": "railway-fallback",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/dispatch")
async def dispatch(request: Request):
    """Dispatch scheduled tasks when called"""
    payload = await request.json()
    await log_to_supabase("dispatch_executed", payload)
    return {"status": "dispatched", "payload": payload}

async def log_to_supabase(action: str, data: dict):
    """Log events to Supabase webhook_logs"""
    if not SUPABASE_KEY:
        return
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/webhook_logs",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "railway-fallback",
                    "payload": data,
                    "forwarded_to": action,
                    "result_status": 200
                },
                timeout=10
            )
    except Exception as e:
        print(f"Supabase log failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
