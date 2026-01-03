
import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

# Mock Supabase Client to avoid actual DB connection errors if offline/missing creds for test
# However, if we have creds, we could try real.
# For robustness in this "Simulation", let's mocking the DB response to prove the LOGIC flow.
# We want to verify: If DB returns X, Concierge returns Y.

from modules.voice.voice_concierge import VoiceConcierge

def test_inbound_flow():
    print("🧪 Starting Voice Nexus Logic Test...\n")
    
    # Mock Credentials
    concierge = VoiceConcierge("https://mock.supabase.co", "mock_key", "mock_vapi")
    
    # 1. Mock DB Lookup for KNOWN CALLER
    mock_contact = {"name": "Test User", "deal_stage": "Closed Won", "phone": "1234567890"}
    
    # Mock the DB chain: table().select().ilike().execute()
    mock_query_builder = MagicMock()
    mock_query_builder.execute.return_value.data = [mock_contact]
    
    concierge.db.table = MagicMock(return_value=MagicMock(
        select=MagicMock(return_value=MagicMock(
            ilike=MagicMock(return_value=mock_query_builder)
        ))
    ))
    
    # Simulate Payload
    payload_known = {
        "message": {"type": "assistant-request"},
        "call": {
            "customer": {"number": "+1234567890"}
        }
    }
    
    print("🔹 Scenario 1: Known Caller")
    response_known = concierge.handle_inbound_webhook(payload_known)
    system_msg = response_known['assistant']['model']['messages'][0]['content']
    print(f"   Result: {system_msg}")
    
    if "Test User" in system_msg and "Closed Won" in system_msg:
        print("   ✅ PASS: Context Injection Successful")
    else:
        print("   ❌ FAIL: Context Missing")
        
    print("-" * 30)

    # 2. Mock DB Lookup for UNKNOWN CALLER
    mock_query_builder_empty = MagicMock()
    mock_query_builder_empty.execute.return_value.data = [] # Empty list
    
    concierge.db.table = MagicMock(return_value=MagicMock(
        select=MagicMock(return_value=MagicMock(
            ilike=MagicMock(return_value=mock_query_builder_empty)
        ))
    ))
    
    payload_unknown = {
        "message": {"type": "assistant-request"},
        "call": {
            "customer": {"number": "+1999999999"}
        }
    }
    
    print("🔹 Scenario 2: Unknown Caller")
    response_unknown = concierge.handle_inbound_webhook(payload_unknown)
    system_msg_unknown = response_unknown['assistant']['model']['messages'][0]['content']
    print(f"   Result: {system_msg_unknown}")
    
    if "new potential client" in system_msg_unknown:
        print("   ✅ PASS: Default Prompt Used")
    else:
        print("   ❌ FAIL: Default Prompt Missing")

    print("\n🏁 Test Complete.")

if __name__ == "__main__":
    test_inbound_flow()
