import modal
from fastapi import Request
import os
import sys
# import user_agent 

# Define the image
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "user-agents")
)

# Modal App Definition
app = modal.App("v2-visitor-analytics")
VAULT = modal.Secret.from_name("agency-vault")

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
async def track_visitor(request: Request):
    try:
        body = await request.json()
    except:
        return {"status": "error", "message": "Invalid JSON"}
        
    # Get header user agent if not in body
    if not body.get("user_agent"):
        body["user_agent"] = request.headers.get("user-agent")
        
    return await process_tracking_event(body)

async def process_tracking_event(body: dict):
    """Core logic separable for testing"""
    import os
    from supabase import create_client
    from user_agents import parse

    # Extract Data
    url = body.get("url")
    referrer = body.get("referrer")
    user_agent_str = body.get("user_agent")
    visitor_id = body.get("visitor_id")
    metadata = body.get("metadata", {})

    # Parse User Agent
    ua = parse(user_agent_str)
    browser = f"{ua.browser.family} {ua.browser.version_string}"
    os_name = f"{ua.os.family} {ua.os.version_string}"
    device_type = "mobile" if ua.is_mobile else "tablet" if ua.is_tablet else "desktop"

    # DB Connection
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return {"status": "error", "message": "Server Config Error"}

    supabase = create_client(supabase_url, supabase_key)

    # Insert
    data = {
        "visitor_id": visitor_id,
        "url": url,
        "referrer": referrer,
        "user_agent": user_agent_str,
        "browser": browser,
        "os": os_name,
        "device_type": device_type,
        "metadata": metadata
    }

    try:
        res = supabase.table("visitor_logs").insert(data).execute()
        return {"status": "success", "id": res.data[0]['id'] if res.data else None}
    except Exception as e:
        print(f"Tracking Error: {e}")
        return {"status": "error", "message": str(e)}

# Local Test Stub
if __name__ == "__main__":
    print("This is a Modal web endpoint. Run `modal serve execution/v2/v2_analytics_api.py` to test.")
