from mcp.server import Server
import requests
import os
import json

# Initialize MCP Server
app = Server("ghl-bridge")

def get_headers():
    token = os.getenv("GHL_PRIVATE_KEY")
    return {
        'Authorization': f'Bearer {token}', 
        'Version': '2021-07-28', 
        'Content-Type': 'application/json'
    }

@app.tool(name="qualify_lead")
def qualify_lead(contact_id: str, budget: float):
    """
    Tags a contact based on budget.
    """
    if budget > 5000:
        tag = "high-value"
    else:
        tag = "nurture"
        
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}/tags"
    try:
        requests.post(url, json={"tags": [tag]}, headers=get_headers())
        return f"Lead {contact_id} tagged as {tag}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("GHL MCP Server Ready.")
