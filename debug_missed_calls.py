import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def diagnose():
    print("🕵️ Investigating Missed Calls...")
    
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Supabase Config Missing")
        return

    try:
        sb = create_client(url, key)
        
        # 1. Check Transcripts (Did Vapi report ANYTHING?)
        print("\n1. Checking Call Transcripts (Last 5)...")
        transcripts = sb.table('call_transcripts').select('*').order('created_at', desc=True).limit(5).execute().data
        if transcripts:
            for t in transcripts:
                print(f"   📞 {t['created_at']} | ID: {t['call_id']} | Ph: {t['phone_number']}")
                print(f"      Summary: {str(t.get('summary'))[:100]}...")
        else:
            print("   ⚠️ No transcripts found.")
            
        # 2. Check System Logs for Errors
        print("\n2. Checking System Logs (ERRORS)...")
        logs = sb.table('system_logs').select('*').eq('level', 'ERROR').order('created_at', desc=True).limit(5).execute().data
        if logs:
            for l in logs:
                print(f"   ❌ {l['created_at']} | {l['message']}")
        else:
            print("   ✅ No recent system errors found.")
            
    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")

if __name__ == "__main__":
    diagnose()
