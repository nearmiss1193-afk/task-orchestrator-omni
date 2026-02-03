
"""
AGENT: WIRING TECH (Back-Office Engineer)
Mission: Autonomously configure GHL backend assets (Links, Forms, Custom Values).
"""

import os
import requests
import json

class WiringTech:
    def __init__(self, token=None):
        # Allow passing token or using env var
        self.token = token or os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }
    
    def create_trigger_link(self, name: str, url: str):
        """
        Creates a tracked 'Trigger Link' in GHL.
        Useful for: 'Click here to book' automation triggers.
        """
        print(f"🔌 Wiring Tech: Creating Trigger Link '{name}' -> {url}")
        
        endpoint = "https://services.leadconnectorhq.com/links"
        payload = {
            "name": name,
            "redirectTo": url
        }
        
        try:
            res = requests.post(endpoint, json=payload, headers=self.headers)
            if res.status_code in [200, 201]:
                print(f"✅ Success: Link Created (ID: {res.json().get('id')})")
                return res.json()
            else:
                print(f"❌ Error {res.status_code}: {res.text}")
                return None
        except Exception as e:
            print(f"❌ Connection Failure: {e}")
            return None

    def create_custom_value(self, name: str, value: str):
        """
        Sets a global variable (Custom Value) for the sub-account.
        """
        print(f"🔌 Wiring Tech: Setting Custom Value '{name}' = '{value}'")
        # Logic would go here
        pass

# Test Interface
if __name__ == "__main__":
    tech = WiringTech()
    # tech.create_trigger_link("Test Booking Link", "https://calendly.com/test")
