
import json

def mock_ghl_webhook(payload):
    print(f"--- WEBHOOK START ---")
    
    if payload is None:
        print("ERR: Payload is None")
        return

    try:
        print(f"Payload: {json.dumps(payload)}")
        
        msg_type = payload.get('type')
        contact_id = payload.get('contact_id') or payload.get('id')
        
        if msg_type == 'ContactUpdate' or not msg_type:
            print("Safe Parsing Start")
            contact_data = payload.get('contact') or {}
            print(f"Contact Data Type: {type(contact_data)}")
            if contact_data is None: 
                print("Contact Data is None explicitly")
                contact_data = {} 
            
            full_name = payload.get('name') or contact_data.get('name', 'Unknown')
            print(f"Name: {full_name}")
            
            tags = payload.get('tags') or contact_data.get('tags') or []
            print(f"Tags: {tags}")
            
            print(f"Parsed: {full_name}")

    except Exception as e:
        print(f"ERR: {str(e)}")
        import traceback
        traceback.print_exc()

# Test Case 1: Standard Shopper Payload
payload_1 = {
    "type": "ContactUpdate",
    "contact_id": "123",
    "contact": {
        "ghl_contact_id": "123",
        "tags": ["trigger-vortex"]
    }
}

# Test Case 2: Null Contact
payload_2 = {
    "type": "ContactUpdate",
    "contact_id": "123",
    "contact": None
}

# Test Case 3: Missing Contact
payload_3 = {
    "type": "ContactUpdate",
    "contact_id": "123"
}

print("Running Case 1:")
mock_ghl_webhook(payload_1)
print("\nRunning Case 2:")
mock_ghl_webhook(payload_2)
print("\nRunning Case 3:")
mock_ghl_webhook(payload_3)
