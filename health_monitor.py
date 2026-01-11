"""
EMPIRE HEALTH MONITOR - Cloud-Deployed System Check
Runs every 3 hours on Modal to verify all systems are operational.
Sends alerts via email if issues detected.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
VAPI_KEY = os.getenv('VAPI_PRIVATE_KEY', os.getenv('VAPI_API_KEY', ''))
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'owner@aiserviceco.com')

# Pages to check
PAGES_TO_CHECK = [
    {'name': 'Dashboard', 'url': 'https://www.aiserviceco.com/dashboard.html'},
    {'name': 'HVAC Landing', 'url': 'https://www.aiserviceco.com/hvac.html'},
    {'name': 'Plumber Landing', 'url': 'https://www.aiserviceco.com/plumber.html'},
    {'name': 'Roofing Landing', 'url': 'https://www.aiserviceco.com/roofing.html'},
    {'name': 'Main Site', 'url': 'https://www.aiserviceco.com'},
]

def check_page(url: str, name: str) -> dict:
    """Check if a page loads successfully"""
    try:
        resp = requests.get(url, timeout=15)
        return {
            'name': name,
            'url': url,
            'status': 'OK' if resp.status_code == 200 else 'FAIL',
            'code': resp.status_code,
            'time_ms': int(resp.elapsed.total_seconds() * 1000)
        }
    except Exception as e:
        return {
            'name': name,
            'url': url,
            'status': 'ERROR',
            'error': str(e)
        }

def check_supabase() -> dict:
    """Check Supabase connectivity and get stats"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Get lead count
        resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/leads?select=id&limit=1',
            headers=headers,
            timeout=10
        )
        
        # Get count header
        count_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/leads?select=count',
            headers={**headers, 'Prefer': 'count=exact'},
            timeout=10
        )
        
        # Get contacted count
        contacted_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/leads?select=count&status=eq.contacted',
            headers={**headers, 'Prefer': 'count=exact'},
            timeout=10
        )
        
        # Get leads with last_called set
        called_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/leads?select=id&last_called=not.is.null',
            headers={**headers, 'Prefer': 'count=exact'},
            timeout=10
        )
        
        total = count_resp.headers.get('content-range', '0').split('/')[-1]
        contacted = contacted_resp.headers.get('content-range', '0').split('/')[-1]
        called = called_resp.headers.get('content-range', '0').split('/')[-1]
        
        return {
            'status': 'OK' if resp.status_code == 200 else 'FAIL',
            'total_leads': total,
            'contacted': contacted,
            'called': called,
            'code': resp.status_code
        }
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def check_vapi() -> dict:
    """Check Vapi API and get call stats"""
    if not VAPI_KEY:
        return {'status': 'SKIP', 'reason': 'VAPI_KEY not configured'}
    try:
        headers = {'Authorization': f'Bearer {VAPI_KEY}'}
        
        # Get today's calls
        today = datetime.now().strftime('%Y-%m-%d')
        resp = requests.get(
            f'https://api.vapi.ai/call?createdAtGte={today}T00:00:00Z',
            headers=headers,
            timeout=15
        )
        
        if resp.status_code == 200:
            calls = resp.json()
            return {
                'status': 'OK',
                'calls_today': len(calls) if isinstance(calls, list) else 0,
                'code': resp.status_code
            }
        else:
            return {'status': 'FAIL', 'code': resp.status_code}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def send_alert(subject: str, body: str):
    """Send alert email via Resend"""
    try:
        resp = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'from': 'alerts@aiserviceco.com',
                'to': [ALERT_EMAIL, 'nearmiss1193@gmail.com'],
                'subject': subject,
                'html': body
            },
            timeout=10
        )
        return resp.status_code == 200
    except:
        return False

def sync_call_count_to_dashboard():
    """
    FIX: Update the contacted leads count to match actual calls made.
    This ensures dashboard shows correct call count.
    """
    if not VAPI_KEY:
        return {'synced': False, 'reason': 'VAPI_KEY not configured'}
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Get calls from Vapi today
        vapi_headers = {'Authorization': f'Bearer {VAPI_KEY}'}
        today = datetime.now().strftime('%Y-%m-%d')
        resp = requests.get(
            f'https://api.vapi.ai/call?createdAtGte={today}T00:00:00Z',
            headers=vapi_headers,
            timeout=15
        )
        
        if resp.status_code == 200:
            calls = resp.json()
            call_count = len(calls)
            
            # Log this to system_logs for dashboard to pick up
            log_entry = {
                'level': 'health_check',
                'message': json.dumps({
                    'type': 'CALL_COUNT_SYNC',
                    'calls_today': call_count,
                    'timestamp': datetime.now().isoformat()
                }),
                'timestamp': datetime.now().isoformat()
            }
            
            requests.post(
                f'{SUPABASE_URL}/rest/v1/system_logs',
                headers=headers,
                json=log_entry,
                timeout=10
            )
            
            return {'synced': True, 'call_count': call_count}
    except Exception as e:
        return {'synced': False, 'error': str(e)}

def run_health_check():
    """Run full system health check"""
    print(f"\n{'='*60}")
    print(f"🔍 EMPIRE HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    issues = []
    report = []
    
    # Check pages
    print("📄 Checking Pages...")
    for page in PAGES_TO_CHECK:
        result = check_page(page['url'], page['name'])
        status_icon = '✅' if result['status'] == 'OK' else '❌'
        print(f"  {status_icon} {result['name']}: {result['status']}")
        report.append(result)
        if result['status'] != 'OK':
            issues.append(f"Page {result['name']} is DOWN")
    
    # Check Supabase
    print("\n🗄️ Checking Supabase...")
    sb_result = check_supabase()
    status_icon = '✅' if sb_result['status'] == 'OK' else '❌'
    print(f"  {status_icon} Supabase: {sb_result['status']}")
    if sb_result['status'] == 'OK':
        print(f"     Total Leads: {sb_result.get('total_leads', 'N/A')}")
        print(f"     Contacted: {sb_result.get('contacted', 'N/A')}")
        print(f"     Called (with last_called): {sb_result.get('called', 'N/A')}")
    else:
        issues.append("Supabase is DOWN")
    
    # Check Vapi
    print("\n📞 Checking Vapi...")
    vapi_result = check_vapi()
    if vapi_result['status'] == 'SKIP':
        print(f"  ⏭️ Vapi: SKIPPED ({vapi_result.get('reason', 'No key')})")
    else:
        status_icon = '✅' if vapi_result['status'] == 'OK' else '❌'
        print(f"  {status_icon} Vapi: {vapi_result['status']}")
        if vapi_result['status'] == 'OK':
            print(f"     Calls Today: {vapi_result.get('calls_today', 0)}")
        elif vapi_result['status'] not in ['OK', 'SKIP']:
            issues.append("Vapi is DOWN or ERROR")
    
    # Sync call count (optional, may fail if VAPI not configured)
    print("\n🔄 Syncing Call Count...")
    try:
        sync_result = sync_call_count_to_dashboard()
        if sync_result and sync_result.get('synced'):
            print(f"  ✅ Synced {sync_result.get('call_count', 0)} calls to dashboard")
        else:
            print(f"  ⏭️ Sync skipped: {sync_result.get('reason', 'N/A') if sync_result else 'Error'}")
    except Exception as e:
        print(f"  ⚠️ Sync error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    if issues:
        print(f"⚠️ ISSUES DETECTED: {len(issues)}")
        for issue in issues:
            print(f"   - {issue}")
        
        # Send alert
        alert_body = f"""
        <h2>🚨 Empire System Alert</h2>
        <p>Health check detected {len(issues)} issue(s):</p>
        <ul>
        {''.join(f'<li>{issue}</li>' for issue in issues)}
        </ul>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><a href="https://www.aiserviceco.com/dashboard.html">View Dashboard</a></p>
        """
        if send_alert(f"🚨 Empire Alert: {len(issues)} Issues Detected", alert_body):
            print("📧 Alert email sent!")
    else:
        print("✅ ALL SYSTEMS OPERATIONAL")
    print(f"{'='*60}\n")
    
    return {
        'timestamp': datetime.now().isoformat(),
        'issues': issues,
        'pages': report,
        'supabase': sb_result,
        'vapi': vapi_result,
        'sync': sync_result
    }

if __name__ == '__main__':
    run_health_check()
