import modal
from .v2_outreach_orchestrator import V2OutreachOrchestrator

# Define the Modal App
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "requests", "anthropic", "openai", "google-generativeai")
)

app = modal.App("v2-empire-orchestrator")
VAULT_V1 = modal.Secret.from_name("agency-vault")
VAULT_V2 = modal.Secret.from_name("v2-vault")

@app.function(image=image, secrets=[VAULT_V1, VAULT_V2], timeout=600)
@modal.web_endpoint(method="POST")
async def trigger_v2_loop():
    """
    HTTP Trigger for the v2.0 Outreach Loop.
    Call this from Supabase Edge Functions.
    """
    print("[MODAL] v2.0 Master Trigger Received.")
    orchestrator = V2OutreachOrchestrator()
    await orchestrator.run_sequence()
    return {"status": "success", "processed": True}

if __name__ == "__main__":
    # For local testing if needed
    import asyncio
    orch = V2OutreachOrchestrator()
    asyncio.run(orch.run_sequence())
