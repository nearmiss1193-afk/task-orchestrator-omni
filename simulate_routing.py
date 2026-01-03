from modules.communications.routing import route_communication
import os

def test_routing():
    print("🚦 TESTING SOVEREIGN ROUTER...")
    
    # Test 1: Simulate Direct Channel (Force Fail/Success based on Env)
    # We deliberately don't set SMTP credentials to trigger fallback (or check mock)
    
    contact = {"email": "test@example.com"}
    content = {"subject": "Test Redundancy", "body": "This is a test."}
    
    res = route_communication(contact, "EMAIL", content)
    
    print(f"\nResult: {res}")
    
    if res['status'] in ['sent', 'simulated']:
        print("✅ Primary Channel OK.")
    elif res['status'] == 'sent_backup':
        print("🛡️ Backup Protocol Engaged (Success).")
    else:
        print("❌ All Channels Failed.")

if __name__ == "__main__":
    test_routing()
