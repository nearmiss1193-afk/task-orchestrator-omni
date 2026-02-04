import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import requests

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SOVEREIGN_TOKEN = "sov-audit-2026-ghost"

def supabase_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = self.headers.get("X-Sovereign-Token")
        if token != SOVEREIGN_TOKEN:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized. Provide X-Sovereign-Token header."}).encode())
            return

        try:
            # Get campaign mode
            campaign = supabase_get("system_state", "key=eq.campaign_mode&select=status")
            mode = campaign[0].get("status") if campaign else "unknown"

            # Get embeds
            embeds = supabase_get("embeds", "select=type,code")
            locked_embeds = {e.get("type"): (e.get("code") or "")[:50] + "..." for e in embeds} if embeds else {}

            # Get last outreach
            touch = supabase_get("outbound_touches", "select=ts&order=ts.desc&limit=1")
            last_outreach = touch[0].get("ts") if touch else None

            # Get lead count
            leads = supabase_get("contacts_master", "select=id&limit=1")

            result = {
                "system_mode": mode,
                "sarah_status": "minimalist_icon_v4",
                "embed_source": "supabase_locked",
                "last_outreach": last_outreach,
                "health": {"supabase": "✅" if leads is not None else "❌", "api": "✅"},
                "locked_embeds": locked_embeds,
                "audit_timestamp": datetime.now().isoformat()
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
