import requests
import json

url = "https://sovereign-empire-api-908fw2.abacusai.app/webhook/system-error"
headers = {
    "Authorization": "Bearer sovereign_abacus_webhook_2026_xyz99",
    "Content-Type": "application/json"
}
payload = {
    "source": "modal",
    "error_type": "ModuleNotFoundError",
    "error_message": "No module named 'this_should_trigger_a_fix'",
    "stack_trace": "Traceback (most recent call last):\n  File \"/app/main.py\", line 1\n    import this_should_trigger_a_fix\nModuleNotFoundError",
    "severity": "high"
}

print("Sending manual POST to Abacus...")
try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print("Status Code:", response.status_code)
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
         print("Response:", response.text)
except Exception as e:
    print("Error:", e)
