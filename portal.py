"""
NEXUS PORTAL - SOVEREIGN PUBLIC INTERFACE
Handles webhooks, websites, and the secured command dashboard.
"""
import sys
import os
if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from core.image_config import portal_image, VAULT
from core.apps import portal_app as app

# Import handlers
from api.webhooks import vapi_webhook, ghl_webhook, dashboard_stats

web_app = FastAPI()

@web_app.post("/vapi_webhook")
async def vapi_route(data: dict):
    return await vapi_webhook(data)

@web_app.post("/ghl_webhook")
async def ghl_route(data: dict):
    return await ghl_webhook(data)

@web_app.get("/dashboard_stats")
async def stats_route():
    return dashboard_stats()

# Mount the public directory for static site hosting
public_path = "/root/public" if os.path.exists("/root/public") else "./public"
web_app.mount("/", StaticFiles(directory=public_path, html=True), name="static")

@app.function(image=portal_image, secrets=[VAULT])
@modal.asgi_app()
def portal_entry():
    return web_app

if __name__ == "__main__":
    print("Nexus Portal - Starting Deployment...")
