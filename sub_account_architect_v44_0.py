
"""
Sub-Account Architect (v44.0)
Handles payment success -> automated client workspace provisioning.
"""

import os, json, requests, datetime
try:
    import stripe
    from flask import Flask, request, abort
except ImportError:
    # Mock for Enviroment where libs not installed
    print("⚠️ Libraries missing. Using MOCK Objects.")
    class MockStripe:
        api_key = None
        class Webhook:
            @staticmethod
            def construct_event(payload, sig, secret):
                return json.loads(payload)
    stripe = MockStripe()
    
    class FlaskMock:
        def __init__(self, name): pass
        def route(self, path, methods):
            def decorator(f): return f
            return decorator
        def run(self, port): print(f" * Running on http://127.0.0.1:{port} (MOCK)")
    
    Flask = FlaskMock
    request = type('obj', (object,), {'data': b'{}', 'headers': {}})
    def abort(code): raise Exception(f"Abort {code}")
    app = Flask(__name__)

# Mock Keys for Local Simulation (if env missing)
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "whsec_mock")
stripe.api_key = STRIPE_SECRET

GHL_API_KEY = os.getenv("GHL_API_KEY", "mock_ghl_key")
GHL_LOCATION = os.getenv("GHL_LOCATION_ID", "mock_location_id")

app = Flask(__name__)

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    # Verification Logic (Skipped for Mock unless configured)
    if STRIPE_SECRET != "sk_test_mock":
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            abort(400)
    else:
        # Trust mock payload
        event = json.loads(payload)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email')
        customer_name = session.get('customer_details', {}).get('name')
        create_ghl_subaccount(customer_name, customer_email)
        
    return {"status": "received"}, 200

def create_ghl_subaccount(name, email):
    print(f"🏗️ Provisioning Sub-Account for {name} ({email})...")
    
    # Mock Request if Key is Mock
    if GHL_API_KEY == "mock_ghl_key":
        response_text = '{"id": "loc_new_123", "name": "' + str(name) + '"}'
        status_code = 200
        print(f"   [SIMULATION] GHL Sub-Account Created: {response_text}")
    else:
        url = "https://rest.gohighlevel.com/v1/locations/" + GHL_LOCATION + "/sub-accounts"
        headers = {"Authorization": "Bearer " + GHL_API_KEY}
        payload = {"name": name, "email": email, "phone": "N/A", "templateId": "default_funnel"}
        try:
            r = requests.post(url, json=payload, headers=headers)
            response_text = r.text
            status_code = r.status_code
        except Exception as e:
            response_text = str(e)
            status_code = 500

    logfile = f"sovereign_digests/SUBACCOUNT_LOG_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    with open(logfile, "w") as f:
        f.write(f"# Sub-Account Creation Report\n**Client:** {name}\n**Email:** {email}\n**Response:** {response_text}\n")
    
    print(f"✅ Log saved to {logfile}")
    
    if status_code == 200:
        launch_workflow(email)

def launch_workflow(email):
    print(f"🚀 Launching Welcome Workflow for {email}...")
    
    if GHL_API_KEY == "mock_ghl_key":
         print("   [SIMULATION] Workflow Triggered.")
    else:
        workflow_url = f"https://rest.gohighlevel.com/v1/locations/{GHL_LOCATION}/workflow-triggers/"
        headers = {"Authorization": "Bearer " + GHL_API_KEY}
        data = {"triggerType": "welcomeSequence", "contactEmail": email}
        try:
            _ = requests.post(workflow_url, json=data, headers=headers)
        except:
            pass

if __name__ == '__main__':
    app.run(port=8000)
