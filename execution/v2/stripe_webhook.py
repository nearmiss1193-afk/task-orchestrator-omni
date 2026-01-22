import modal
from fastapi import Request
import os
import sys

# Define Image
image = (
    modal.Image.debian_slim()
    .pip_install("stripe", "supabase", "python-dotenv", "requests")
)

app = modal.App("v2-stripe-webhook")
VAULT = modal.Secret.from_name("agency-vault")

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
async def stripe_webhook(request: Request):
    import stripe
    from execution.v2.executors import EmpireExecutors
    import os

    # Config
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    if not stripe.api_key:
        return {"status": "error", "message": "Missing Stripe Key"}

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        # Verify Signature (if secret provided)
        if webhook_secret and sig_header:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # Fallback for dev/test without signature verification
            import json
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
    except Exception as e:
        print(f"⚠️ Webhook Error: {e}")
        return {"status": "error", "message": str(e)}

    # Handle Event
    if event['type'] == 'payment_intent.succeeded':
        # Simple Payment
        intent = event['data']['object']
        amount = intent['amount'] / 100.0
        email = intent.get('receipt_email') 
        # Note: PaymentIntents don't always have email if not passed.
        
        print(f"💰 Payment Received: ${amount} from {email}")
        
        if email:
            executes_logic(email, amount)

    elif event['type'] == 'checkout.session.completed':
        # Checkout (Preferred)
        session = event['data']['object']
        email = session.get('customer_details', {}).get('email')
        amount = (session.get('amount_total') or 0) / 100.0
        
        print(f"💰 Checkout Complete: ${amount} from {email}")
        
        if email:
            executes_logic(email, amount)

    return {"status": "success"}

def executes_logic(email, amount):
    """
    Business Logic: Update DB -> Onboard
    """
    from execution.v2.executors import EmpireExecutors
    from supabase import create_client
    
    # Init Executors
    executor = EmpireExecutors()
    
    if not executor.db_connected:
        print("❌ DB Not connected")
        return

    # 1. Find Customer
    res = executor.supabase.table("contacts_master").select("*").eq("email", email).execute()
    contact = res.data[0] if res.data else None
    
    if contact:
        print(f"✅ Found existing contact: {contact.get('ghl_contact_id')}")
        # 2. Update Status
        executor.update_database("contacts_master", contact['id'], {
            "status": "customer",
            "last_order_value": amount
        })
    else:
        print(f"✨ New Contact (Walk-in): {email}")
        # Optionally create contact here
    
    # 3. Trigger Onboarding
    executor.onboard_customer(email, amount)
