import modal
import os
import stripe
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Define App
app = modal.App("checkout-api-fix")

# Lightweight Image
image = modal.Image.debian_slim().pip_install("fastapi", "stripe")

# Secret
VAULT = modal.Secret.from_name("agency-vault")

# FastAPI with CORS
web_app = FastAPI()

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@web_app.post("/create-checkout-session")
async def create_btn_checkout(request: Request):
    """
    ENDPOINT: Create Stripe Checkout Session ($99)
    """
    try:
        body = await request.json()
        
        # Load Key
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        if not stripe.api_key:
            return {"error": "Missing Stripe Key"}

        # Create ad-hoc session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'AI Service Co - Basic Plan',
                    },
                    'unit_amount': 9900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://aiserviceco.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://aiserviceco.com/cancel',
        )
        return {"url": session.url}
    except Exception as e:
        print(f"Stripe Error: {e}")
        return {"error": str(e)}

@app.function(image=image, secrets=[VAULT])
@modal.asgi_app()
def api():
    return web_app
