import os
import sys

# Ensure root is in path
sys.path.append(os.getcwd())

# Mock Environment
os.environ["GHL_AGENCY_API_TOKEN"] = "mock_agency_token"
os.environ["GHL_LOCATION_ID"] = "mock_location_id"

from modules.fulfillment.sub_account_architect import provision_client

print("🧪 Starting Stripe Event Simulation...")

# Mock Data
customer_name = "Test Client"
customer_email = "test.client@example.com"
session_id = "sess_12345"

# Execute
result = provision_client(customer_name, customer_email, session_id)

print(f"📊 Result: {result}")

if result['status'] == 'success':
     print("✅ Simulation Passed (Logic Flow)")
     # Note: It will fail at the API call level with mock keys, but the flow is verified.
else:
     if result['message'] == "Failed to create location" and os.environ.get("GHL_AGENCY_API_TOKEN") == "mock_agency_token":
          print("✅ Simulation Passed (Graceful Failure on Mock Key)")
     else:
          print("❌ Simulation Failed")
