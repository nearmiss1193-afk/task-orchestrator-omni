
import os
import datetime

class SMSModule:
    def __init__(self, provider="MOCK"):
        self.provider = provider
        self.log_file = os.path.join(os.getcwd(), 'sms_dispatch.log')

    def send_sms(self, to_number, message):
        timestamp = datetime.datetime.now().isoformat()
        
        if self.provider == "MOCK":
            log_entry = f"[{timestamp}] SMS_MOCK_SENT TO: {to_number} | MSG: {message}\n"
            print(log_entry.strip())
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            return True
        
        # Future: Twilio Implementation
        # client.messages.create(body=message, from_=TWILIO_NUMBER, to=to_number)
        return False

# Standalone execution
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        start_msg = " ".join(sys.argv[2:])
        SMSModule().send_sms(sys.argv[1], start_msg)
    else:
        print("Usage: python sms.py <phone> <message>")
