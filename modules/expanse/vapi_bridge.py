
import os
import json
import requests

class VapiBridge:
    """
    Sovereign Stack: VAPI Voice Bridge
    Enables autonomous outbound AI voice calling.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("VAPI_PRIVATE_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json"
        }

    def start_outbound_call(self, phone_number: str, script_context: str, assistant_id: str = None):
        """
        Initiates an AI call to a prospect.
        """
        if not self.api_key:
            print("⚠️ [VapiBridge] No API Key found. Running in SIMULATION mode.")
            return {
                "status": "simulated",
                "action": "outbound_call",
                "target": phone_number,
                "message": f"Simulated call with context: {script_context[:50]}..."
            }

        payload = {
            "phoneNumber": phone_number,
            "assistantId": assistant_id or os.environ.get("VAPI_ASSISTANT_ID"),
            "customer": {
                "number": phone_number,
            },
            "assistantOverrides": {
                "variableValues": {
                    "context": script_context
                }
            }
        }

        try:
            resp = requests.post(f"{self.base_url}/call/phone", json=payload, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    bridge = VapiBridge()
    # print(bridge.start_outbound_call("+15550000000", "Hey this is Spartan."))
