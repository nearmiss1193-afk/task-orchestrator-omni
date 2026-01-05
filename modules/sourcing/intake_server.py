
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Senior Placement Intake Engine")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LEADS_FILE = "active_leads.json"

class Lead(BaseModel):
    name: str
    phone: str
    budget: int
    care_needs: str # e.g., "Bathing, Memory Care"
    preferred_city: str
    email: str

@app.get("/")
def health():
    return {"status": "Intake Engine Online"}

@app.post("/submit-lead")
def submit_lead(lead: Lead):
    print(f"📥 New Lead Received: {lead.name} (${lead.budget})")
    
    # Save to JSON (Simulating Database)
    leads = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r") as f:
            try:
                leads = json.load(f)
            except:
                leads = []
    
    lead_data = lead.dict()
    lead_data["status"] = "NEW"
    lead_data["timestamp"] = datetime.now().isoformat()
    
    leads.append(lead_data)
    
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)
        
    return {"status": "received", "lead_count": len(leads)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Intake Server running on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
