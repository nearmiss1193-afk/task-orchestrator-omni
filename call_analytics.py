"""
CALL ANALYTICS DASHBOARD
========================
Real-time call analytics and reporting.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY', '')
VAPI_BASE_URL = "https://api.vapi.ai"

app = Flask(__name__)


def get_vapi_headers() -> dict:
    return {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }


def get_calls(days: int = 7, limit: int = 100) -> list:
    """Get calls from Vapi"""
    
    if not VAPI_PRIVATE_KEY:
        return mock_calls()
    
    try:
        response = requests.get(
            f"{VAPI_BASE_URL}/call",
            headers=get_vapi_headers(),
            params={"limit": limit}
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def analyze_calls(calls: list) -> dict:
    """Analyze call data for insights"""
    
    if not calls:
        calls = mock_calls()
    
    total_calls = len(calls)
    
    # Duration analysis
    durations = [c.get('duration', 0) for c in calls if c.get('duration')]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Status breakdown
    status_counts = defaultdict(int)
    for call in calls:
        status_counts[call.get('status', 'unknown')] += 1
    
    # Direction breakdown
    inbound = sum(1 for c in calls if c.get('direction') == 'inbound')
    outbound = total_calls - inbound
    
    # Hourly distribution
    hourly = defaultdict(int)
    for call in calls:
        if call.get('createdAt'):
            try:
                hour = datetime.fromisoformat(call['createdAt'].replace('Z', '+00:00')).hour
                hourly[hour] += 1
            except:
                pass
    
    # Peak hours
    peak_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Booking rate (calls that resulted in appointments)
    bookings = sum(1 for c in calls if 'book' in json.dumps(c.get('messages', [])).lower())
    booking_rate = (bookings / total_calls * 100) if total_calls > 0 else 0
    
    return {
        "period": f"Last {len(calls)} calls",
        "total_calls": total_calls,
        "inbound": inbound,
        "outbound": outbound,
        "avg_duration_seconds": round(avg_duration, 1),
        "avg_duration_formatted": f"{int(avg_duration // 60)}m {int(avg_duration % 60)}s",
        "status_breakdown": dict(status_counts),
        "peak_hours": [{"hour": h, "calls": c} for h, c in peak_hours],
        "estimated_bookings": bookings,
        "booking_rate": f"{booking_rate:.1f}%",
        "analyzed_at": datetime.now().isoformat()
    }


def get_call_transcripts(call_id: str) -> dict:
    """Get transcript for a specific call"""
    
    if not VAPI_PRIVATE_KEY:
        return {"mock": True, "transcript": "Sample transcript..."}
    
    try:
        response = requests.get(
            f"{VAPI_BASE_URL}/call/{call_id}",
            headers=get_vapi_headers()
        )
        
        if response.status_code == 200:
            call = response.json()
            return {
                "call_id": call_id,
                "transcript": call.get('transcript', ''),
                "messages": call.get('messages', []),
                "duration": call.get('duration'),
                "status": call.get('status')
            }
        return {"error": "Call not found"}
    except Exception as e:
        return {"error": str(e)}


def get_daily_summary() -> dict:
    """Get summary for today"""
    
    calls = get_calls(days=1)
    analysis = analyze_calls(calls)
    
    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        **analysis
    }


def generate_report(days: int = 7) -> str:
    """Generate a text report"""
    
    calls = get_calls(days=days)
    analysis = analyze_calls(calls)
    
    report = f"""
📊 CALL ANALYTICS REPORT
========================
Period: Last {days} days
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

OVERVIEW
--------
Total Calls: {analysis['total_calls']}
  • Inbound: {analysis['inbound']}
  • Outbound: {analysis['outbound']}

PERFORMANCE
-----------
Avg Duration: {analysis['avg_duration_formatted']}
Booking Rate: {analysis['booking_rate']}
Est. Bookings: {analysis['estimated_bookings']}

PEAK HOURS
----------
"""
    
    for ph in analysis.get('peak_hours', []):
        hour = ph['hour']
        time_str = f"{hour}:00" if hour >= 10 else f"0{hour}:00"
        report += f"  • {time_str} - {ph['calls']} calls\n"
    
    report += """
STATUS BREAKDOWN
----------------
"""
    
    for status, count in analysis.get('status_breakdown', {}).items():
        report += f"  • {status}: {count}\n"
    
    return report


# Mock data
def mock_calls() -> list:
    return [
        {"id": "c1", "duration": 180, "status": "completed", "direction": "inbound", "createdAt": "2026-01-07T10:30:00Z"},
        {"id": "c2", "duration": 45, "status": "completed", "direction": "outbound", "createdAt": "2026-01-07T11:00:00Z"},
        {"id": "c3", "duration": 0, "status": "missed", "direction": "inbound", "createdAt": "2026-01-07T14:30:00Z"},
        {"id": "c4", "duration": 240, "status": "completed", "direction": "inbound", "createdAt": "2026-01-07T15:00:00Z"},
        {"id": "c5", "duration": 120, "status": "completed", "direction": "outbound", "createdAt": "2026-01-07T16:30:00Z"},
    ]


# API endpoints
@app.route('/api/analytics')
def api_analytics():
    return jsonify(analyze_calls(get_calls()))


@app.route('/api/daily')
def api_daily():
    return jsonify(get_daily_summary())


@app.route('/api/calls')
def api_calls():
    return jsonify(get_calls())


@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "call_analytics"})


DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Call Analytics</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #2563eb; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }
        .card { background: #1e293b; border-radius: 12px; padding: 24px; }
        .card h3 { color: #94a3b8; font-size: 14px; margin: 0 0 8px; }
        .card .value { font-size: 36px; font-weight: 700; color: #2563eb; }
        .card .sub { color: #64748b; font-size: 12px; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Call Analytics Dashboard</h1>
        <div class="grid">
            <div class="card">
                <h3>Total Calls</h3>
                <div class="value" id="total">--</div>
            </div>
            <div class="card">
                <h3>Avg Duration</h3>
                <div class="value" id="duration">--</div>
            </div>
            <div class="card">
                <h3>Booking Rate</h3>
                <div class="value" id="booking">--</div>
            </div>
            <div class="card">
                <h3>Est. Bookings</h3>
                <div class="value" id="bookings">--</div>
            </div>
        </div>
    </div>
    <script>
        fetch('/api/analytics').then(r => r.json()).then(data => {
            document.getElementById('total').textContent = data.total_calls;
            document.getElementById('duration').textContent = data.avg_duration_formatted;
            document.getElementById('booking').textContent = data.booking_rate;
            document.getElementById('bookings').textContent = data.estimated_bookings;
        });
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(generate_report())
    elif len(sys.argv) > 1 and sys.argv[1] == "serve":
        print("[ANALYTICS] Starting dashboard on port 5053...")
        app.run(host='0.0.0.0', port=5053, debug=False)
    else:
        print("Call Analytics Summary:")
        print(json.dumps(analyze_calls(get_calls()), indent=2))
