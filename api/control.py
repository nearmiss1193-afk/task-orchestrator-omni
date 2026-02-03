from http.server import BaseHTTPRequestHandler
import json
import requests
import os
from urllib.parse import urlparse

API_BASE = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request("GET")

    def do_POST(self):
        self.proxy_request("POST")

    def proxy_request(self, method):
        try:
            # Extract the path after /api/control
            parsed_path = urlparse(self.path)
            subpath = parsed_path.path.replace('/api/control', '', 1)
            
            target_url = f"{API_BASE}/api/control{subpath}"
            if parsed_path.query:
                target_url += f"?{parsed_path.query}"

            headers = {k: v for k, v in self.headers.items() if k.lower() not in ['host', 'content-length']}
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            if method == "GET":
                response = requests.get(target_url, headers=headers, timeout=10)
            else:
                response = requests.post(target_url, headers=headers, data=body, timeout=10)

            self.send_response(response.status_code)
            for k, v in response.headers.items():
                if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                    self.send_header(k, v)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(response.content)))
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "status": "control_proxy_failed"}).encode())
