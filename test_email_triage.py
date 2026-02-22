from workers.email_triage import handle_inbound_email
import os

def run_email_test():
    # Make sure we don't actually send emails during the test
    # by temporarily disabling the Resend API key or printing the payload
    # For now, handle_inbound_email will just print the intent if RESEND_API_KEY is not set
    # or if we are just logging the result
    
    sender = "testlead@example.com"
    
    print("\n--- Test 1: General Email ---")
    sub1 = "Question about your services"
    bod1 = "Hi Sarah, do you guys do local SEO or just AI voice stuff?"
    res1 = handle_inbound_email(sender, sub1, bod1)
    print(f"Result: {res1}")
    
    print("\n--- Test 2: Booking Email ---")
    sub2 = "Ready to start"
    bod2 = "I saw the audit you sent. I'd like to schedule a time to talk this week."
    res2 = handle_inbound_email(sender, sub2, bod2)
    print(f"Result: {res2}")

if __name__ == "__main__":
    run_email_test()
