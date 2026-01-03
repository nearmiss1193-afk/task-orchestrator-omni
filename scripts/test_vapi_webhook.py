
import requests
import json

URL = "http://localhost:3000/api/vapi/webhook"

mock_payload = {
  "message": {
    "type": "tool-calls",
    "toolCalls": [
      {
        "id": "test_call_1",
        "function": {
           "name": "get_dashboard_stats",
           "arguments": "{}"
        }
      },
      {
        "id": "test_call_2",
        "function": {
           "name": "execute_command",
           "arguments": "{\"command\": \"Simulate Solar Launch\"}"
        }
      }
    ]
  }
}

try:
    print(f"Sending Mock Tool Call to {URL}...")
    r = requests.post(URL, json=mock_payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
