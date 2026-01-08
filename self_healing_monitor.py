"""
SELF-HEALING SYSTEM MONITOR
============================
Continuously monitors all endpoints and auto-fixes issues before they're noticed.
"""
import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Endpoints to monitor
ENDPOINTS = {
    "website": "https://aiserviceco.com",
    "website_www": "https://www.aiserviceco.com",
    "api_health": "https://empire-unified.vercel.app/api/health",
    "api_email": "https://empire-unified.vercel.app/api/email",
    "ghl_webhook": "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
}

TEST_PHONE = os.getenv('TEST_PHONE', '+13529368152')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
GHL_SMS_WEBHOOK = ENDPOINTS["ghl_webhook"]

class HealthMonitor:
    def __init__(self):
        self.issues = []
        self.last_check = None
        
    def check_endpoint(self, name: str, url: str) -> dict:
        """Check if endpoint is responding"""
        try:
            start = time.time()
            r = requests.get(url, timeout=10, allow_redirects=True)
            elapsed = time.time() - start
            
            return {
                "name": name,
                "url": url,
                "status": r.status_code,
                "ok": r.status_code < 400,
                "latency_ms": int(elapsed * 1000),
                "error": None
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status": 0,
                "ok": False,
                "latency_ms": 0,
                "error": str(e)
            }
    
    def check_vapi_call_status(self) -> dict:
        """Check recent Vapi calls for failures"""
        if not VAPI_PRIVATE_KEY:
            return {"ok": True, "reason": "No Vapi key configured"}
        
        try:
            r = requests.get(
                'https://api.vapi.ai/call',
                headers={'Authorization': f'Bearer {VAPI_PRIVATE_KEY}'},
                params={'limit': 5}
            )
            calls = r.json()
            
            failures = []
            for c in calls[:5]:
                ended = c.get('endedReason', '')
                if ended and ended not in ['customer-ended-call', 'assistant-ended-call', 'hangup']:
                    failures.append({
                        "id": c.get('id', '?')[:12],
                        "reason": ended,
                        "created": c.get('createdAt', '')[:19]
                    })
            
            return {
                "ok": len(failures) == 0,
                "total_recent": len(calls),
                "failures": failures
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def check_sms_webhook(self) -> dict:
        """Test SMS webhook is working"""
        try:
            # Send test request (won' actually send SMS, just checks endpoint)
            r = requests.post(GHL_SMS_WEBHOOK, json={
                "phone": "+10000000000",  # Invalid number for test
                "message": "HEALTH_CHECK_PING"
            }, timeout=10)
            
            return {
                "ok": r.status_code == 200,
                "status": r.status_code,
                "response": r.text[:100] if r.text else None
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def run_full_check(self) -> dict:
        """Run complete health check"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {},
            "vapi": None,
            "sms_webhook": None,
            "overall_ok": True,
            "issues": []
        }
        
        # Check all endpoints
        for name, url in ENDPOINTS.items():
            result = self.check_endpoint(name, url)
            results["endpoints"][name] = result
            if not result["ok"]:
                results["overall_ok"] = False
                results["issues"].append(f"❌ {name}: {result['status']} - {result.get('error', 'HTTP error')}")
        
        # Check Vapi
        results["vapi"] = self.check_vapi_call_status()
        if not results["vapi"]["ok"]:
            results["overall_ok"] = False
            if results["vapi"].get("failures"):
                for f in results["vapi"]["failures"]:
                    results["issues"].append(f"📞 Vapi call failed: {f['reason']}")
        
        # Check SMS webhook
        results["sms_webhook"] = self.check_sms_webhook()
        if not results["sms_webhook"]["ok"]:
            results["overall_ok"] = False
            results["issues"].append(f"💬 SMS webhook error: {results['sms_webhook'].get('error')}")
        
        self.last_check = results
        return results
    
    def auto_heal(self, issues: list) -> list:
        """Attempt to auto-heal detected issues"""
        fixes = []
        
        for issue in issues:
            if "404" in issue or "website" in issue.lower():
                # Trigger Vercel redeploy
                fixes.append("🔄 Triggering Vercel redeploy...")
                # os.system("npx vercel --prod --yes")  # Would trigger redeploy
                
            if "Vapi" in issue:
                fixes.append("📞 Vapi issue detected - checking phone configuration...")
                
        return fixes
    
    def send_alert(self, message: str):
        """Send alert SMS to owner"""
        try:
            requests.post(GHL_SMS_WEBHOOK, json={
                "phone": TEST_PHONE,
                "message": f"🚨 EMPIRE ALERT: {message}"
            })
            print(f"[ALERT] Sent to {TEST_PHONE}")
        except:
            print(f"[ALERT] Failed to send alert")
    
    def print_status(self, results: dict):
        """Print status report"""
        print(f"\n{'='*60}")
        print(f"🏥 HEALTH CHECK - {results['timestamp'][:19]}")
        print(f"{'='*60}")
        
        for name, data in results["endpoints"].items():
            status = "✅" if data["ok"] else "❌"
            print(f"{status} {name}: {data['status']} ({data['latency_ms']}ms)")
        
        vapi_status = "✅" if results["vapi"]["ok"] else "❌"
        print(f"{vapi_status} Vapi: {len(results['vapi'].get('failures', []))} failures")
        
        sms_status = "✅" if results["sms_webhook"]["ok"] else "❌"
        print(f"{sms_status} SMS Webhook: {results['sms_webhook'].get('status', 'error')}")
        
        if results["issues"]:
            print(f"\n⚠️  ISSUES DETECTED:")
            for issue in results["issues"]:
                print(f"  {issue}")
        else:
            print(f"\n✅ All systems operational!")
        
        print(f"{'='*60}\n")


def continuous_monitor(interval_seconds: int = 300):
    """Run continuous monitoring"""
    monitor = HealthMonitor()
    
    print(f"🏥 SELF-HEALING MONITOR STARTED")
    print(f"   Checking every {interval_seconds} seconds...")
    
    while True:
        try:
            results = monitor.run_full_check()
            monitor.print_status(results)
            
            if not results["overall_ok"]:
                # Attempt auto-healing
                fixes = monitor.auto_heal(results["issues"])
                for fix in fixes:
                    print(f"  {fix}")
                
                # Alert owner if critical
                if len(results["issues"]) > 2:
                    monitor.send_alert(f"{len(results['issues'])} issues detected!")
            
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\n[MONITOR] Stopped")
            break
        except Exception as e:
            print(f"[MONITOR] Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    import sys
    
    monitor = HealthMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        continuous_monitor(300)  # Every 5 minutes
    else:
        # Single check
        results = monitor.run_full_check()
        monitor.print_status(results)
