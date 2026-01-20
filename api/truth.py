from http.server import BaseHTTPRequestHandler
import json
import requests
import os

API_BASE = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Proxy to the Modal /api/truth endpoint
            target_url = f"{API_BASE}/api/truth"
            response = requests.get(target_url, timeout=5)
            
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
