import os
import time

def simulate_sale():
    print("\n=== EMPIRE SIMULATION: NEW CUSTOMER SALE ===")
    print("This script simulates a webhook event from GHL/Stripe indicating a new sale.")
    print("Use this to test 'Process Phase 3' (Onboarding & Alerts) without spending money.\n")
    
    name = input("Enter Mock Customer Name (default: Tester): ") or "Tester"
    phone = input("Enter Mock Phone (for AI Call): ")
    email = input("Enter Mock Email: ")

    print(f"\nSimulating Sale for {name} ($297 Growth Plan)...")
    time.sleep(1)
    print("... Stripe Charge: SUCCESS")
    time.sleep(1)
    print(f"... GHL Contact Updated: {email}")
    time.sleep(1)
    print("... Triggering 'Onboarding Workflow'...")
    time.sleep(1)
    
    print("\n[ACTION REQUIRED] Check your GHL Dashboard or Email/SMS.")
    print(f"If the system connects to Vapi, an AI call would be dispatched to {phone} now.")
    
    # In a real scenario, this would POST to the webhook URL. 
    # Since we are Sovereign-Lite, we print the instructions.
    print(f"\nTo actually trigger the AI Call, run:")
    print(f"python modules/communications/onboarding_trigger.py --phone {phone} --name {name}")

if __name__ == "__main__":
    simulate_sale()
