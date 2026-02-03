from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse

# Modal API Base URL
API_BASE = 'https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run'

class handler(BaseHTTPRequestHandler):
    """
    Vercel Proxy for Webhooks.
    Provides a stable domain (aiserviceco.com) for GHL/Vapi webhooks.
    """
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Path logic: /api/webhook/status -> https://...modal.run/webhook/sms/status
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Routing Map
        routing = {
            '/api/webhook/inbound': '/webhook/sms/inbound',
            '/api/webhook/status': '/webhook/sms/status',
            '/api/webhook/vapi': '/webhook/vapi',
            '/api/webhook/ghl': '/webhook/ghl'
        }
        
        target_subpath = routing.get(path)
        if not target_subpath:
            # Fallback: just append everything after /api/webhook
            target_subpath = path.replace('/api/webhook', '', 1)
        
        target_url = f"{API_BASE}{target_subpath}"
        
        try:
            # Proxy headers (avoid host conflicts)
            headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
            
            # Forward to Modal
            resp = requests.post(target_url, data=post_data, headers=headers, timeout=30)
            
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.content)
            
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "target": target_url}).encode())

    def do_GET(self):
        # Health check for proxy
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "proxy_online", "target_base": API_BASE}).encode())
