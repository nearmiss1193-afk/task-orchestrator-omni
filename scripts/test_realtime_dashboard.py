import os
import time
from dotenv import load_dotenv
from modules.database.supabase_client import get_supabase

def test_realtime_feed():
    load_dotenv()
    sb = get_supabase()
    
    print("🚀 Simulating Real-time Outreach Event...")
    
    # 1. Simulate SMS
    res_sms = sb.table("outbound_touches").insert({
        "phone": "+19999999999",
        "channel": "sms",
        "status": "sent",
        "company": "Real-time Test Co",
        "payload": {"content": "Hello from the test suite!"}
    }).execute()
    print("✅ SMS touch inserted")

    # 2. Simulate Sarah Transcript
    res_call = sb.table("conversation_logs").insert({
        "channel": "voice",
        "direction": "outbound",
        "content": "This is a real-time call transcript test. Sarah is identifying a high-value HVAC prospect.",
        "sarah_response": "Scheduling follow-up.",
        "metadata": {"test": True}
    }).execute()
    print("✅ Call transcript inserted")

    # 3. Simulate Social Broadcast
    res_social = sb.table("conversation_logs").insert({
        "channel": "social",
        "direction": "outbound",
        "content": "Automating the empire in real-time. #SovereignAI",
        "metadata": {"platform": "twitter", "source": "Verification Test"}
    }).execute()
    print("✅ Social log inserted via conversation_logs")

    print("\n🏁 Check the Vercel/Local dashboard. All 3 events should be visible without refresh.")

if __name__ == "__main__":
    test_realtime_feed()
