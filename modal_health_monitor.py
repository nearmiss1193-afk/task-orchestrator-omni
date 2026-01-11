"""
MODAL HEALTH MONITOR DEPLOYMENT
Runs health check every 3 hours automatically from the cloud.
Deploy with: modal deploy modal_health_monitor.py
"""
import modal
import os

# Create Modal app
app = modal.App("empire-health-monitor")

# Create image with dependencies
image = modal.Image.debian_slim().pip_install(
    "requests",
    "python-dotenv"
)

# Store secrets in Modal
secrets = modal.Secret.from_dict({
    "NEXT_PUBLIC_SUPABASE_URL": os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""),
    "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    "RESEND_API_KEY": os.getenv("RESEND_API_KEY", ""),
    "VAPI_PRIVATE_KEY": os.getenv("VAPI_PRIVATE_KEY", ""),
    "ALERT_EMAIL": "owner@aiserviceco.com"
})

@app.function(
    image=image,
    secrets=[secrets],
    schedule=modal.Cron("0 */3 * * *")  # Every 3 hours
)
def health_check():
    """Run health check every 3 hours"""
    import requests
    import json
    from datetime import datetime
    
    SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
    VAPI_KEY = os.environ.get('VAPI_PRIVATE_KEY', '')
    ALERT_EMAIL = os.environ.get('ALERT_EMAIL', 'owner@aiserviceco.com')
    
    PAGES = [
        ('Dashboard', 'https://www.aiserviceco.com/dashboard.html'),
        ('HVAC', 'https://www.aiserviceco.com/hvac.html'),
        ('Plumber', 'https://www.aiserviceco.com/plumber.html'),
        ('Roofing', 'https://www.aiserviceco.com/roofing.html'),
        ('Main', 'https://www.aiserviceco.com'),
    ]
    
    issues = []
    results = []
    
    # Check pages
    for name, url in PAGES:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                issues.append(f"{name} returned {resp.status_code}")
            results.append({'name': name, 'status': resp.status_code})
        except Exception as e:
            issues.append(f"{name} failed: {str(e)}")
            results.append({'name': name, 'status': 'ERROR'})
    
    # Check Supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Prefer': 'count=exact'
            }
            resp = requests.get(
                f'{SUPABASE_URL}/rest/v1/leads?select=count',
                headers=headers,
                timeout=10
            )
            total = resp.headers.get('content-range', '0').split('/')[-1]
            results.append({'name': 'Supabase', 'status': 'OK', 'leads': total})
        except Exception as e:
            issues.append(f"Supabase failed: {str(e)}")
    
    # Check Vapi
    if VAPI_KEY:
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            resp = requests.get(
                f'https://api.vapi.ai/call?createdAtGte={today}T00:00:00Z',
                headers={'Authorization': f'Bearer {VAPI_KEY}'},
                timeout=15
            )
            if resp.status_code == 200:
                calls = resp.json()
                call_count = len(calls) if isinstance(calls, list) else 0
                results.append({'name': 'Vapi', 'status': 'OK', 'calls_today': call_count})
            else:
                issues.append(f"Vapi returned {resp.status_code}")
        except Exception as e:
            issues.append(f"Vapi failed: {str(e)}")
    
    # Send alert if issues
    if issues and RESEND_API_KEY:
        alert_body = f"""
        <h2>🚨 Empire Health Alert</h2>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Issues detected:</p>
        <ul>{''.join(f'<li>{i}</li>' for i in issues)}</ul>
        <p><a href="https://www.aiserviceco.com/dashboard.html">View Dashboard</a></p>
        """
        try:
            requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {RESEND_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': 'alerts@aiserviceco.com',
                    'to': [ALERT_EMAIL, 'nearmiss1193@gmail.com'],
                    'subject': f'🚨 Empire Alert: {len(issues)} Issues',
                    'html': alert_body
                },
                timeout=10
            )
        except:
            pass
    
    print(f"Health check complete: {len(issues)} issues, {len(results)} checks")
    return {'issues': issues, 'results': results, 'timestamp': datetime.now().isoformat()}

@app.local_entrypoint()
def main():
    """Run health check manually"""
    result = health_check.remote()
    print(f"Result: {result}")

if __name__ == "__main__":
    # For local testing
    from dotenv import load_dotenv
    load_dotenv()
    print("Run with: modal deploy modal_health_monitor.py")
