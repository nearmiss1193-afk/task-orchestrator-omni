
# ... (Previous existing code) ...

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
def clickup_interaction(payload: dict):
    """
    MISSION 39: CLICKUP WEBHOOK RECEIVER
    Endpoint for ClickUp Automations to notify Sovereign Agent.
    """
    from modules.governor.sovereign_ops_agent import SovereignOpsAgent
    
    # 1. Initialize Agent
    agent = SovereignOpsAgent()
    
    # 2. Process Event
    response = agent.handle_webhook_event(payload)
    
    return response

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 12 * * *")) # 07:00 EST
def sovereign_ops_cron():
    """
    MISSION 39: DAILY OPS PULSE
    Runs the Sovereign Pulse Reporter every morning.
    """
    from modules.governor.sovereign_ops_agent import SovereignOpsAgent
    agent = SovereignOpsAgent()
    agent.run_daily_pulse()
