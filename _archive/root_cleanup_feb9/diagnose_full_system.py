"""
ANTIGRAVITY v5.0 - System Diagnostic Script
Runs all verification checks per Section 1 of the Master Prompt
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_env_vars():
    """Check critical environment variables"""
    print("\n" + "="*60)
    print("🔍 ENVIRONMENT VARIABLES CHECK")
    print("="*60)
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "GHL_LOCATION_ID",
        "GHL_CLIENT_ID",
        "GHL_CLIENT_SECRET"
    ]
    
    missing = []
    for var in required_vars:
        val = os.environ.get(var)
        if val:
            if "KEY" in var or "SECRET" in var:
                print(f"✅ {var}: {val[:10]}...{val[-5:]}")
            else:
                print(f"✅ {var}: {val}")
        else:
            print(f"❌ {var}: MISSING")
            missing.append(var)
    
    return len(missing) == 0

def check_supabase_connection():
    """Test Supabase database connectivity"""
    print("\n" + "="*60)
    print("🔍 SUPABASE CONNECTION CHECK")
    print("="*60)
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        # CRITICAL: Use service_role key (Master Prompt Section 2)
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Missing Supabase credentials")
            return False
        
        print(f"🔗 URL: {url}")
        print(f"🔑 Key type: {'SERVICE_ROLE' if 'SERVICE_ROLE' in str(os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')) else 'ANON'}")
        
        sb = create_client(url, key)
        
        # Test contacts_master access
        result = sb.table("contacts_master").select("id,full_name,status", count="exact").limit(5).execute()
        
        print(f"✅ Database connected: {result.count} total contacts")
        if result.data:
            print(f"   Sample contacts:")
            for contact in result.data[:3]:
                print(f"   - {contact.get('full_name', 'Unknown')} ({contact.get('status', 'no status')})")
        
        return result.count > 0
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_outreach_activity():
    """Check recent outreach activity (Master Prompt Section 1)"""
    print("\n" + "="*60)
    print("🔍 OUTREACH ACTIVITY CHECK (Last 30 min)")
    print("="*60)
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        
        sb = create_client(url, key)
        
        # The ONLY truth test (Master Prompt Section 1)
        result = sb.table("outbound_touches").select("*", count="exact").gte(
            "ts", 
            (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        ).execute()
        
        count = result.count or 0
        
        if count > 0:
            print(f"✅ WORKING: {count} outreach messages sent in last 30 min")
            if result.data:
                latest = result.data[0]
                print(f"   Latest: {latest.get('channel', 'unknown')} to {latest.get('contact_id', 'unknown')}")
        else:
            print(f"❌ NOT WORKING: 0 outreach messages in last 30 min")
            print(f"   System may be broken regardless of deploy status")
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Outreach check failed: {e}")
        return False

def check_system_health():
    """Check system_health_log for heartbeat"""
    print("\n" + "="*60)
    print("🔍 SYSTEM HEARTBEAT CHECK")
    print("="*60)
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        
        sb = create_client(url, key)
        
        result = sb.table("system_health_log").select("*").order("checked_at", desc=True).limit(5).execute()
        
        if result.data:
            latest = result.data[0]
            checked_at = latest.get('checked_at')
            status = latest.get('status')
            
            print(f"✅ Latest heartbeat: {checked_at}")
            print(f"   Status: {status}")
            
            # Check if heartbeat is recent (within 15 min)
            from dateutil import parser
            heartbeat_time = parser.parse(checked_at)
            age_minutes = (datetime.now(timezone.utc) - heartbeat_time).total_seconds() / 60
            
            if age_minutes < 15:
                print(f"   ✅ Heartbeat is fresh ({age_minutes:.1f} min old)")
                return True
            else:
                print(f"   ⚠️ Heartbeat is stale ({age_minutes:.1f} min old)")
                return False
        else:
            print("❌ No heartbeat records found")
            return False
            
    except Exception as e:
        print(f"❌ Heartbeat check failed: {e}")
        return False

def check_campaign_mode():
    """Check campaign_mode status"""
    print("\n" + "="*60)
    print("🔍 CAMPAIGN MODE CHECK")
    print("="*60)
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        
        sb = create_client(url, key)
        
        result = sb.table("system_state").select("*").eq("key", "campaign_mode").execute()
        
        if result.data:
            mode = result.data[0].get('status')
            print(f"   Campaign mode: {mode}")
            
            if mode == "working":
                print(f"   ✅ Campaign is ACTIVE")
                return True
            else:
                print(f"   ❌ Campaign is NOT active (status: {mode})")
                return False
        else:
            print("❌ No campaign_mode record found")
            return False
            
    except Exception as e:
        print(f"❌ Campaign mode check failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("\n" + "="*80)
    print("⚫ ANTIGRAVITY v5.0 - SYSTEM DIAGNOSTIC")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {
        "Environment Variables": check_env_vars(),
        "Supabase Connection": check_supabase_connection(),
        "Campaign Mode": check_campaign_mode(),
        "System Heartbeat": check_system_health(),
        "Outreach Activity": check_outreach_activity()
    }
    
    print("\n" + "="*80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*80)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ SYSTEM STATUS: VERIFIED WORKING")
    else:
        print("❌ SYSTEM STATUS: FAILED")
        print("\nFailed checks indicate system is NOT working, regardless of deploy exit code.")
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
