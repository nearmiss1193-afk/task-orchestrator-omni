"""
Health Check - Vercel Serverless Function
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = {
            "status": "ok",
            "services": ["email_webhook", "vapi_webhook", "analytics"],
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
