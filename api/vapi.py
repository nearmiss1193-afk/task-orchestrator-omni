"""
Vapi Call Webhook Handler - Vercel Serverless Function
Logs calls to Supabase and triggers SSE call.logged events
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
from datetime import datetime


GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def log_call_to_supabase(call_data: dict):
    """Store call record to Supabase call_logs table"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[VAPI] Supabase not configured, skipping DB log")
        return None
    
    try:
        payload = json.dumps(call_data).encode()
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/call_logs",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "return=representation"
            },
            method="POST"
        )
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        print(f"[VAPI] Logged to Supabase: {call_data.get('call_id')}")
        return result
    except Exception as e:
        print(f"[VAPI] Supabase log error: {e}")
        return None


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
                msg = data.get('message', {})
                call_obj = msg.get('call', {})
                
                # Extract stable keys for call.logged payload
                call_record = {
                    "call_id": call_id if call_id != 'unknown' else None,
                    "from_number": call_obj.get('customer', {}).get('number') or call_obj.get('from') or None,
                    "to_number": call_obj.get('phoneNumber', {}).get('number') or call_obj.get('to') or None,
                    "timestamp": call_obj.get('startedAt') or datetime.now().isoformat(),
                    "disposition": ended_reason or call_obj.get('status') or 'completed',
                    "summary": msg.get('summary') or msg.get('artifact', {}).get('summary') or None,
                    "transcript": msg.get('transcript') or msg.get('artifact', {}).get('transcript') or None,
                    "duration_seconds": call_obj.get('duration') or msg.get('durationSeconds') or 0,
                    "assistant_id": call_obj.get('assistantId') or None,
                    "created_at": datetime.now().isoformat()
                }
                
                # Log to Supabase
                log_call_to_supabase(call_record)
                
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
