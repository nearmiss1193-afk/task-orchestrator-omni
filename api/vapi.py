"""
Vapi Call Webhook Handler - Vercel Serverless Function
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
from datetime import datetime


GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            call_status = data.get('message', {}).get('type', 'unknown')
            call_id = data.get('message', {}).get('call', {}).get('id', 'unknown')
            
            print(f"[VAPI] {call_status} - Call: {call_id}")
            
            # Forward missed calls
            if call_status in ['end-of-call-report', 'hang']:
                ended_reason = data.get('message', {}).get('endedReason', '')
                if ended_reason in ['no-answer', 'busy', 'failed']:
                    backup_phone = os.environ.get('TEST_PHONE', '+13529368152')
                    
                    try:
                        payload = json.dumps({
                            "phone": backup_phone,
                            "message": f"📞 Missed call! Reason: {ended_reason}. Call back ASAP."
                        }).encode()
                        
                        req = urllib.request.Request(
                            GHL_SMS_WEBHOOK,
                            data=payload,
                            headers={'Content-Type': 'application/json'}
                        )
                        urllib.request.urlopen(req, timeout=10)
                    except:
                        pass
            
            response = {
                "status": "received",
                "call_status": call_status,
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "vapi_webhook"}).encode())
