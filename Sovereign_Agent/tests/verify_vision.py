
import requests
import os

try:
    print("📸 Requesting Screenshot from Cortex...")
    res = requests.post("http://localhost:8000/execute", json={
        "action": "screenshot",
        "parameters": {"filename": "vision_test.png"}
    })
    
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    
    if res.status_code == 200 and os.path.exists("vision_test.png"):
        print("✅ Vision Test PASSED. Image saved.")
    else:
        print("❌ Vision Test FAILED.")

except Exception as e:
    print(f"❌ Error: {e}")
