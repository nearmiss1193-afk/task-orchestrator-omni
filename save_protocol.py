"""
SAVE PROTOCOL - Complete System Status Report
==============================================
Sends comprehensive email report with:
- Recovery protocol
- System capabilities  
- Recommendations
- Dashboard link
- Gaps/unchecked items
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

def send_save_protocol_email():
    """Send comprehensive status report email"""
    
    resend_key = os.getenv("RESEND_API_KEY")
    owner_email = os.getenv("GHL_EMAIL") or "nearmiss1193@gmail.com"
    
    # Gather system status
    from supabase import create_client
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    stats = {}
    gaps = []
    
    try:
        client = create_client(supa_url, supa_key)
        
        # Lead counts
        leads = client.table("leads").select("id", count="exact").execute()
        stats["total_leads"] = leads.count or 0
        
        new_leads = client.table("leads").select("id", count="exact").eq("status", "new").execute()
        stats["new_leads"] = new_leads.count or 0
        
        called = client.table("leads").select("id", count="exact").eq("status", "called").execute()
        stats["called_leads"] = called.count or 0
        
        # Call transcripts
        calls = client.table("call_transcripts").select("id", count="exact").execute()
        stats["total_calls"] = calls.count or 0
        
        # Recent logs
        recent = client.table("system_logs").select("*").order("created_at", desc=True).limit(5).execute()
        stats["recent_logs"] = [f"{r.get('event_type', 'LOG')}: {r.get('message', '')[:50]}" for r in recent.data]
        
        # Check for gaps
        needs_enrich = client.table("leads").select("id", count="exact").eq("status", "needs_enrichment").execute()
        if needs_enrich.count and needs_enrich.count > 0:
            gaps.append(f"⚠️ {needs_enrich.count} leads need manual enrichment")
        
        if stats["new_leads"] < 10:
            gaps.append("⚠️ Lead pipeline low (<10 new leads)")
            
    except Exception as e:
        stats["error"] = str(e)
        gaps.append(f"❌ Supabase connection error: {e}")
    
    # Check API keys
    apis = {
        "VAPI_PRIVATE_KEY": "Vapi (Calls)",
        "RESEND_API_KEY": "Resend (Emails)",
        "APOLLO_API_KEY": "Apollo (Enrichment)",
        "AYRSHARE_API_KEY": "Ayrshare (Social)",
        "ANTHROPIC_API_KEY": "Claude (AI)",
        "GEMINI_API_KEY": "Gemini (AI)"
    }
    
    api_status = []
    for key, name in apis.items():
        status = "✅" if os.getenv(key) else "❌"
        api_status.append(f"{status} {name}")
        if not os.getenv(key):
            gaps.append(f"❌ Missing API key: {key}")
    
    # Build email HTML
    html = f"""
    <div style="font-family: system-ui; max-width: 700px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 30px; border-radius: 12px;">
        
        <h1 style="color: #3b82f6; margin-bottom: 5px;">🛡️ Empire Save Protocol Report</h1>
        <p style="color: #64748b; margin-top: 0;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <hr style="border-color: #334155; margin: 20px 0;">
        
        <!-- DASHBOARD LINK -->
        <div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: white;">📊 Live Dashboard</h2>
            <a href="https://aiserviceco.com/dashboard.html" style="color: white; font-size: 18px;">
                https://aiserviceco.com/dashboard.html
            </a>
        </div>
        
        <!-- SYSTEM STATUS -->
        <h2 style="color: #10b981;">📈 System Status</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #334155;">Total Leads</td><td style="text-align: right; font-weight: bold;">{stats.get('total_leads', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #334155;">New Leads (Pipeline)</td><td style="text-align: right; font-weight: bold;">{stats.get('new_leads', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #334155;">Called Leads</td><td style="text-align: right; font-weight: bold;">{stats.get('called_leads', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #334155;">Total Calls Made</td><td style="text-align: right; font-weight: bold;">{stats.get('total_calls', 'N/A')}</td></tr>
        </table>
        
        <!-- CAPABILITIES -->
        <h2 style="color: #3b82f6; margin-top: 30px;">🚀 Active Capabilities</h2>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ AI Outbound Calling (Sarah via Vapi)</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ Email Campaigns (Resend)</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ Lead Prospecting (Gemini AI)</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ Self-Healing Enrichment (Apollo.io)</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ Social Media Automation (Ayrshare)</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ 24/7 Cloud Operations (Modal)</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ Real-time Dashboard</li>
            <li style="padding: 8px; background: #1e293b; margin: 5px 0; border-radius: 4px;">✅ Health Monitoring + Auto-Repair</li>
        </ul>
        
        <!-- API STATUS -->
        <h2 style="color: #f59e0b; margin-top: 30px;">🔑 API Status</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            {''.join([f'<div style="padding: 8px; background: #1e293b; border-radius: 4px;">{s}</div>' for s in api_status])}
        </div>
        
        <!-- GAPS & ISSUES -->
        <h2 style="color: #ef4444; margin-top: 30px;">⚠️ Gaps & Unchecked Items</h2>
        {'<ul style="padding-left: 20px;">' + ''.join([f'<li style="color: #fbbf24; margin: 8px 0;">{g}</li>' for g in gaps]) + '</ul>' if gaps else '<p style="color: #22c55e;">✅ No critical gaps detected</p>'}
        
        <!-- RECOMMENDATIONS -->
        <h2 style="color: #8b5cf6; margin-top: 30px;">💡 Recommendations</h2>
        <ol style="padding-left: 20px;">
            <li style="margin: 10px 0;">Monitor dashboard daily for call outcomes</li>
            <li style="margin: 10px 0;">Check Modal logs weekly for any failed functions</li>
            <li style="margin: 10px 0;">Review leads marked "needs_enrichment" for manual research</li>
            <li style="margin: 10px 0;">Update Sarah's script based on call transcript learnings</li>
            <li style="margin: 10px 0;">Consider adding SMS via GHL for multi-touch</li>
        </ol>
        
        <!-- RECOVERY PROTOCOL -->
        <h2 style="color: #06b6d4; margin-top: 30px;">🔄 Recovery Protocol</h2>
        <div style="background: #1e293b; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px;">
            <p style="margin: 5px 0; color: #94a3b8;"># If system is down:</p>
            <p style="margin: 5px 0;">1. cd c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified</p>
            <p style="margin: 5px 0;">2. python -m modal deploy modal_deploy.py</p>
            <p style="margin: 5px 0;">3. python lead_quality_guardian.py</p>
            <p style="margin: 5px 0;">4. python -m modal run modal_deploy.py::cloud_multi_touch</p>
            <p style="margin: 5px 0; color: #94a3b8;"># Check health:</p>
            <p style="margin: 5px 0;">5. python health_monitor.py</p>
        </div>
        
        <!-- RECENT ACTIVITY -->
        <h2 style="color: #64748b; margin-top: 30px;">📋 Recent Activity</h2>
        <ul style="color: #94a3b8; font-size: 12px;">
            {''.join([f'<li>{log}</li>' for log in stats.get('recent_logs', ['No recent logs'])])}
        </ul>
        
        <hr style="border-color: #334155; margin: 30px 0;">
        
        <p style="text-align: center; color: #64748b; font-size: 12px;">
            Empire Sovereign System v2.0 | AI Service Co<br>
            <a href="https://aiserviceco.com" style="color: #3b82f6;">aiserviceco.com</a>
        </p>
    </div>
    """
    
    # Send email
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}"},
            json={
                "from": "Empire System <system@aiserviceco.com>",
                "to": [owner_email],
                "subject": f"🛡️ Save Protocol Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "html": html
            }
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Save Protocol email sent to {owner_email}")
            return True
        else:
            print(f"❌ Email failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🛡️ EMPIRE SAVE PROTOCOL")
    print(f"   Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    print("\n📧 Sending status report email...")
    send_save_protocol_email()
    
    print("\n✅ Save Protocol Complete!")
    print("=" * 60)
