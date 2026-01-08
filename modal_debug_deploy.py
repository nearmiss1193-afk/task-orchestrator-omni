import modal
import os

app = modal.App("empire-sovereign-webhook-test")

image = modal.Image.debian_slim().pip_install("flask", "requests", "python-dotenv", "supabase", "fastapi")

@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))]
)
@modal.web_endpoint(method="POST", label="vapi-webhook")
def vapi_webhook(data: dict):
    print(f"WEBHOOK TEST: {data}")
    return {"status": "ok"}
