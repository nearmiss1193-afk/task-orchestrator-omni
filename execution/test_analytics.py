import asyncio
import sys
import os
sys.path.append(os.getcwd())
from unittest.mock import MagicMock
from execution.v2.v2_analytics_api import process_tracking_event

async def test_tracking():
    print("Testing Analytics API...")
    
    payload = {
        "url": "https://example.com/landing",
        "referrer": "google.com",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "visitor_id": "test-visitor-123",
        "metadata": {"source": "test_script"}
    }
    
    # req = MockRequest(payload, {}) # No longer needed
    
    try:
        from dotenv import load_dotenv
        load_dotenv('.env.local')
        
        res = await process_tracking_event(payload)
        print(f"Result: {res}")
        
        if res.get("status") == "success":
            print("✅ Tracking Successful")
        else:
            print("❌ Tracking Failed")
            
    except ImportError as e:
        print(f"❌ Missing Dependency: {e}")
        print("Run: pip install user-agents")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tracking())
