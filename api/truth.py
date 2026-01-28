from http.server import BaseHTTPRequestHandler
import json
import os
try:
    import requests
except ImportError as e:
    requests = None
    IMPORT_ERROR = str(e)

API_BASE = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if requests is None:
                raise ImportError(f"Requests library missing. Error: {IMPORT_ERROR}")

            # Proxy to the Modal /api/truth endpoint
            target_url = f"{API_BASE}/api/truth"
            
            # Inject Admin Token for the proxy
            headers = {
                "X-Admin-Token": os.environ.get("ADMIN_TOKEN", "aiserviceco-admin-2026")
            }
            
            response = requests.get(target_url, headers=headers, timeout=5)
            
            self.send_response(response.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            err = {"error": str(e), "status": "proxy_failed"}
            self.wfile.write(json.dumps(err).encode())
