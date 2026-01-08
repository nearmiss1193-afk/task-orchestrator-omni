"""
MODAL TRAINING DEPLOYMENT
Runs knowledge crawler in the cloud 24/7
Prevents local system freezes
"""

import modal

# Create Modal app
app = modal.App("empire-training")

# Define the image with dependencies
image = modal.Image.debian_slim().pip_install(
    "requests",
    "schedule",
    "python-dotenv"
)


@app.function(
    image=image,
    schedule=modal.Cron("0 * * * *"),  # Run every hour
    timeout=3600
)
def hourly_training():
    """Run training every hour in the cloud"""
    import requests
    from datetime import datetime
    import json
    from pathlib import Path
    
    KNOWLEDGE_DIR = Path("/root/knowledge_base")
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    
    DOCS = {
        "vapi": "https://docs.vapi.ai",
        "resend": "https://resend.com/docs",
        "supabase": "https://supabase.com/docs",
        "openai": "https://platform.openai.com/docs",
        "ghl": "https://highlevel.stoplight.io/docs/integrations"
    }
    
    print(f"[TRAINING] Starting cloud training at {datetime.now()}")
    
    for tool, url in DOCS.items():
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "EmpireBot/1.0"})
            if r.status_code == 200:
                tool_dir = KNOWLEDGE_DIR / tool
                tool_dir.mkdir(exist_ok=True)
                with open(tool_dir / f"{datetime.now().strftime('%Y%m%d_%H')}.json", "w") as f:
                    json.dump({"url": url, "content": r.text[:50000], "fetched": datetime.now().isoformat()}, f)
                print(f"[LEARNED] {tool}")
        except Exception as e:
            print(f"[ERROR] {tool}: {e}")
    
    return {"status": "complete", "time": datetime.now().isoformat()}


@app.function(image=image)
def send_ghl_sms(phone: str, message: str):
    """Send SMS via GHL webhook from cloud"""
    import requests
    
    WEBHOOK_URL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    
    r = requests.post(WEBHOOK_URL, json={"phone": phone, "message": message})
    print(f"SMS webhook: {r.status_code}")
    return {"status": r.status_code, "phone": phone}


@app.local_entrypoint()
def main():
    """Deploy and test"""
    print("Deploying Empire Training to Modal...")
    result = hourly_training.remote()
    print(f"Training result: {result}")
    
    # Test SMS
    sms_result = send_ghl_sms.remote("+13529368152", "Test SMS from Modal Cloud")
    print(f"SMS result: {sms_result}")


if __name__ == "__main__":
    main()
