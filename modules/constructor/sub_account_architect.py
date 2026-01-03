import os
import requests
import json
import time

class SubAccountArchitect:
    """
    MISSION: BRIDGE BUILDER
    Automates the creation of GHL Locations (Sub-Accounts) upon Stripe Purchase.
    """
    def __init__(self, agency_token=None):
        self.token = agency_token or os.environ.get("GHL_AGENCY_API_TOKEN")
        self.api_url = "https://services.leadconnectorhq.com/locations/"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }

    def process_purchase(self, stripe_payload):
        """
        Main Sentinel Logic:
        1. Extract Customer Info
        2. Determine Niche (Snapshot)
        3. Attempt Creation (Retry 2x)
        4. Fallback to Alert
        """
        try:
            print("[Architect] Processing Stripe Event...")
            data = self._extract_data(stripe_payload)
            
            if not data:
                print("[Architect] Invalid Data or Non-Purchase Event.")
                return {"status": "skipped"}

            # Attempt Creation (Max 2 Retries)
            for attempt in range(3):
                result = self._create_ghl_location(data)
                if result.get("success"):
                    return {"status": "created", "location_id": result.get("id")}
                
                print(f"[Architect] Attempt {attempt+1} failed: {result.get('error')}")
                time.sleep(2) # Backoff

            # FAILED 3x -> FALLBACK
            self._trigger_fallback(data)
            return {"status": "fallback_triggered"}

        except Exception as e:
            print(f"[Architect] Critical Error: {e}")
            self._trigger_fallback({"error": str(e), "raw": str(stripe_payload)[:100]})
            return {"status": "error"}

    def _extract_data(self, payload):
        """Parse Stripe Session Object"""
        try:
            obj = payload.get('data', {}).get('object', {})
            customer = obj.get('customer_details', {})
            
            # Map Product to Niche (Simplistic for now)
            # In production, check line_items or metadata
            niche = "Generic Service"
            
            return {
                "name": customer.get('name') or "Unknown Owner",
                "email": customer.get('email'),
                "phone": customer.get('phone'),
                "address": customer.get('address', {}).get('line1', '123 Main St'),
                "city": customer.get('address', {}).get('city', 'Anytown'),
                "state": customer.get('address', {}).get('state', 'FL'),
                "zip": customer.get('address', {}).get('postal_code', '00000'),
                "country": customer.get('address', {}).get('country', 'US'),
                "business_name": "New Client Business", # Stripe doesn't always have this, generic fallback
                "niche": niche
            }
        except:
            return None

    def _create_ghl_location(self, data):
        """Call GHL Agency API to Create Location"""
        payload = {
            "name": data['business_name'],
            "phone": data['phone'],
            "email": data['email'],
            "address": data['address'],
            "city": data['city'],
            "state": data['state'],
            "country": data['country'],
            "postalCode": data['zip'],
            "website": "https://pending-setup.com",
            "timezone": "America/New_York",
            "settings": {
                "allowDuplicateContact": True, # Simplify
                "allowDuplicateOpportunity": True
            }
            # "snapshotId": "..." # TODO: Add Snapshot Logic based on Niche
        }
        
        try:
            res = requests.post(self.api_url, json=payload, headers=self.headers)
            if res.status_code == 201:
                loc_id = res.json().get('id')
                print(f"[Architect] Success! Created Location: {loc_id}")
                return {"success": True, "id": loc_id}
            else:
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _trigger_fallback(self, data):
        """Manual Intervention Alert"""
        try:
            # We assume deploy.py exposes send_live_alert or we re-implement simplistic version
            # Ideally imported, but to keep module pure, we'll just print for now 
            # or rely on the caller (deploy.py) to handle the returned status.
            print(f"⚠️ [ARCHITECT FALLBACK] PLEASE MANUALLY SETUP: {data}")
            # Real alerting happens in the deploy wrapper
        except:
            pass
