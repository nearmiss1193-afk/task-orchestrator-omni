from workers.ai_reply import generate_sarah_reply

def run_test():
    phone = "+15550001234"
    name = "Test User"
    
    # 1. Test General Inquiry
    print("\n--- Test 1: General Inquiry ---")
    msg1 = "Hey Sarah, what are your hours?"
    reply1 = generate_sarah_reply(phone, msg1, name)
    print(f"Reply: {reply1}")
    
    # 2. Test Booking Intent
    print("\n--- Test 2: Booking Intent ---")
    msg2 = "I'm interested, how do I schedule a call with Dan?"
    reply2 = generate_sarah_reply(phone, msg2, name)
    print(f"Reply: {reply2}")

if __name__ == "__main__":
    run_test()
