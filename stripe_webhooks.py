"""
STRIPE WEBHOOK HANDLER
======================
Handles Stripe payment events.
Triggers onboarding workflow on successful checkout.
"""

import os
import json
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
NOTIFY_PHONE = os.getenv('TEST_PHONE', '+13529368152')

# Payment log
PAYMENTS_LOG = "payments.json"


@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # Verify signature if secret is configured
    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError:
            return jsonify({"error": "Invalid signature"}), 400
    else:
        event = json.loads(payload)
    
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    print(f"[STRIPE] Event: {event_type}")
    
    # Handle specific events
    if event_type == 'checkout.session.completed':
        handle_checkout_completed(data)
    elif event_type == 'payment_intent.succeeded':
        handle_payment_succeeded(data)
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_failed(data)
    elif event_type == 'customer.subscription.created':
        handle_subscription_created(data)
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_cancelled(data)
    
    return jsonify({"status": "received"})


def handle_checkout_completed(session: dict):
    """Handle successful checkout"""
    
    customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
    customer_name = session.get('customer_details', {}).get('name', 'New Customer')
    amount = session.get('amount_total', 0) / 100  # Convert from cents
    
    print(f"[CHECKOUT] {customer_name} ({customer_email}) - ${amount}")
    
    # Log payment
    log_payment({
        "type": "checkout_completed",
        "email": customer_email,
        "name": customer_name,
        "amount": amount,
        "session_id": session.get('id'),
        "timestamp": datetime.now().isoformat()
    })
    
    # Notify via SMS
    notify_payment(f"🎉 NEW SALE! {customer_name} - ${amount:.2f}")
    
    # Trigger onboarding workflow
    trigger_onboarding(customer_email, customer_name)


def handle_payment_succeeded(intent: dict):
    """Handle successful payment"""
    amount = intent.get('amount', 0) / 100
    print(f"[PAYMENT] Succeeded: ${amount}")


def handle_payment_failed(intent: dict):
    """Handle failed payment"""
    email = intent.get('receipt_email', 'Unknown')
    print(f"[PAYMENT] Failed for {email}")
    notify_payment(f"⚠️ Payment failed: {email}")


def handle_subscription_created(subscription: dict):
    """Handle new subscription"""
    plan = subscription.get('plan', {}).get('nickname', 'Unknown Plan')
    print(f"[SUBSCRIPTION] Created: {plan}")
    notify_payment(f"📅 New subscription: {plan}")


def handle_subscription_cancelled(subscription: dict):
    """Handle cancelled subscription"""
    print(f"[SUBSCRIPTION] Cancelled")
    notify_payment("❌ Subscription cancelled")


def notify_payment(message: str):
    """Send SMS notification about payment event"""
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": NOTIFY_PHONE,
            "message": message
        })
        print(f"[SMS] Notification sent")
    except Exception as e:
        print(f"[ERROR] SMS failed: {e}")


def trigger_onboarding(email: str, name: str):
    """Trigger customer onboarding workflow"""
    print(f"[ONBOARDING] Triggering for {name} ({email})")
    # This would call the GHL onboarding workflow
    # For now, just log it


def log_payment(payment: dict):
    """Log payment to file"""
    try:
        with open(PAYMENTS_LOG, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(payment)
    
    with open(PAYMENTS_LOG, "w") as f:
        json.dump(logs, f, indent=2)


def get_payment_stats():
    """Get payment statistics"""
    try:
        with open(PAYMENTS_LOG, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    
    total_revenue = sum(p.get('amount', 0) for p in logs)
    return {
        "total_payments": len(logs),
        "total_revenue": total_revenue,
        "payments": logs[-10:]  # Last 10
    }


@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(get_payment_stats())


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "stripe-webhooks"})


if __name__ == "__main__":
    print("Starting Stripe Webhook Server...")
    print(f"Notify phone: {NOTIFY_PHONE}")
    print("Configure Stripe webhook to POST to /webhook/stripe")
    app.run(host='0.0.0.0', port=5052, debug=True)
