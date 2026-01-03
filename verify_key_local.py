
import stripe
import sys

# The key provided by the user
KEY = "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"

def test_key():
    print(f"Testing Key: {KEY[:8]}...{KEY[-4:]}")
    stripe.api_key = KEY.strip()
    
    try:
        # Try to list products or create a dummy session to verify permissions
        # Creating a session is what we actually want to do in production
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Verification Test'},
                    'unit_amount': 100, # $1.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
        print("✅ SUCCESS: Key is valid. Session created.")
        print(f"Session ID: {session.id}")
        return True
    except Exception as e:
        print(f"❌ FAILURE: {e}")
        return False

if __name__ == "__main__":
    if test_key():
        sys.exit(0)
    else:
        sys.exit(1)
