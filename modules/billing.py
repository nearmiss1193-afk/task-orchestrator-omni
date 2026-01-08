import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(email, setup_price_id, subscription_price_id, connect_account_id=None):
    """
    Creates a checkout session for 'Setup Fee Now, Subscription in 30 Days'.
    """
    # 1. Create Customer
    customer = stripe.Customer.create(email=email)
    
    # 2. Create Subscription Schedule
    # We don't use the standard 'subscription' mode in checkout because we have a custom schedule.
    # Instead, we create the schedule via API, then create a generic Payment Link or Checkout Session 
    # that references this. 
    # ACTUALLY, Checkout supports 'subscription_data' but not complex schedules directly in one easy go 
    # for "Setup Fee" as a separate phase smoothly without code.
    # STRATEGY: 
    # We will use 'mode=subscription' with a 'trial_period_days=30' and a 'setup_fee' line item.
    # This is simpler than Schedules and achieves the requirement "Charge setup now, start sub later".
    
    success_url = os.getenv("APP_URL", "http://localhost:8501") + "/success"
    cancel_url = os.getenv("APP_URL", "http://localhost:8501") + "/cancel"


    session_config = {
        "customer": customer.id,
        "mode": "subscription",
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price": subscription_price_id, # The monthly recurring price
            }
        ],
        "subscription_data": {
            "trial_period_days": 30, # Delay usage for 30 days
            "metadata": {"type": "saas_subscription"}
        },
        "success_url": success_url,
        "cancel_url": cancel_url,
    }
    
    # Add Setup Fee as a one-time line item
    # Note: In 'subscription' mode, additional one-time line items are allowed.
    if setup_price_id:
        session_config["line_items"].append({
            "price": setup_price_id,
            "quantity": 1
        })
        
    # Connect Platform Fees (if applicable)
    if connect_account_id:
        session_config["subscription_data"]["transfer_data"] = {
            "destination": connect_account_id
        }
        # Application Fee percent or amount must be set on the Price object or here
        session_config["subscription_data"]["application_fee_percent"] = 10.0

    session = stripe.checkout.Session.create(**session_config)
    return session.url

def get_connect_onboarding_link(email):
    """
    Generates a link for a sub-account to onboard via Stripe Express.
    """
    # 1. Create Account
    account = stripe.Account.create(
        type="express",
        email=email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
    )
    
    # 2. Create Account Link
    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url=os.getenv("APP_URL") + "/reauth",
        return_url=os.getenv("APP_URL") + "/dashboard",
        type="account_onboarding",
    )
    
    return account_link.url
