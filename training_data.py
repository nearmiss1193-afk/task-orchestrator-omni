"""
TRAINING DATA SCHEMA - Learning examples for continuous improvement
Stores conversation outcomes for pattern extraction
"""
import requests
from datetime import datetime
import json

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# Training Data Schema
TRAINING_DATA_SCHEMA = {
    "conversations": {
        "id": "uuid",
        "phone": "string",
        "raw_text": "string",
        "scenario": "inbound|outbound|objection|booking|follow_up",
        "outcome": "booked|sent_link|follow_up|not_fit|opted_out|escalated",
        "takeaways": ["string"],
        "emotional_cues": {
            "likability_markers": ["friendly", "helpful", "understanding"],
            "fear_indicators": ["worried", "concerned", "losing"],
            "desire_indicators": ["want", "growth", "improve"],
            "objection_types": ["price", "timing", "authority"],
            "closing_triggers": ["interested", "sounds good", "book"],
            "persuasion_elements": ["because", "imagine", "results"]
        },
        "agent": "sarah|christina",
        "created_at": "timestamp",
        "learning_extracted": "boolean"
    }
}


def extract_emotional_cues(text: str) -> dict:
    """Extract emotional and persuasion cues from conversation text"""
    text_lower = text.lower()
    
    cues = {
        "likability_markers": [],
        "fear_indicators": [],
        "desire_indicators": [],
        "objection_types": [],
        "closing_triggers": [],
        "persuasion_elements": []
    }
    
    # Likability markers
    likability_words = ["friendly", "helpful", "understanding", "thanks", "appreciate", "great", "awesome"]
    cues["likability_markers"] = [w for w in likability_words if w in text_lower]
    
    # Fear indicators
    fear_words = ["worried", "concerned", "afraid", "losing", "missing", "falling behind", "competition"]
    cues["fear_indicators"] = [w for w in fear_words if w in text_lower]
    
    # Desire indicators
    desire_words = ["want", "wish", "hope", "grow", "more leads", "more bookings", "improve", "better"]
    cues["desire_indicators"] = [w for w in desire_words if w in text_lower]
    
    # Objection types
    if any(w in text_lower for w in ["price", "cost", "expensive", "afford", "budget"]):
        cues["objection_types"].append("price")
    if any(w in text_lower for w in ["busy", "not now", "later", "time"]):
        cues["objection_types"].append("timing")
    if any(w in text_lower for w in ["boss", "partner", "decision", "check with"]):
        cues["objection_types"].append("authority")
    if any(w in text_lower for w in ["already have", "using", "current"]):
        cues["objection_types"].append("current_solution")
    
    # Closing triggers
    closing_words = ["interested", "sounds good", "tell me more", "let's do it", "book", "sign up", "ready"]
    cues["closing_triggers"] = [w for w in closing_words if w in text_lower]
    
    # Persuasion elements
    persuasion_words = ["because", "imagine", "results", "proven", "guarantee", "easy", "quick"]
    cues["persuasion_elements"] = [w for w in persuasion_words if w in text_lower]
    
    return cues


def extract_takeaways(text: str, outcome: str) -> list:
    """Extract key takeaways from conversation outcome"""
    takeaways = []
    
    if outcome == "booked":
        takeaways.append("Successful booking achieved")
        if "quick" in text.lower() or "15 min" in text.lower():
            takeaways.append("Short time commitment was effective")
    
    elif outcome == "sent_link":
        takeaways.append("Interest expressed but not committed")
        takeaways.append("Follow-up sequence should activate")
    
    elif outcome == "opted_out":
        takeaways.append("Lead opted out - do not contact")
        if "stop" in text.lower():
            takeaways.append("Explicit STOP request")
    
    elif outcome == "not_fit":
        takeaways.append("Lead not qualified")
    
    elif outcome == "escalated":
        takeaways.append("Required human intervention")
    
    return takeaways


def store_training_data(phone: str, raw_text: str, scenario: str, 
                        outcome: str, agent: str = "sarah") -> bool:
    """Store conversation as training data"""
    
    emotional_cues = extract_emotional_cues(raw_text)
    takeaways = extract_takeaways(raw_text, outcome)
    
    data = {
        "phone": phone,
        "raw_text": raw_text,
        "scenario": scenario,
        "outcome": outcome,
        "takeaways": json.dumps(takeaways),
        "emotional_cues": json.dumps(emotional_cues),
        "agent": agent,
        "learning_extracted": False
    }
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/training_data",
            headers=HEADERS,
            json=data,
            timeout=15
        )
        return r.status_code in [200, 201]
    except:
        return False


def get_training_examples(scenario: str = None, outcome: str = None, limit: int = 10) -> list:
    """Retrieve training examples for analysis"""
    params = {"limit": limit, "order": "created_at.desc"}
    
    if scenario:
        params["scenario"] = f"eq.{scenario}"
    if outcome:
        params["outcome"] = f"eq.{outcome}"
    
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/training_data",
            headers=HEADERS,
            params=params,
            timeout=15
        )
        return r.json() if r.status_code == 200 else []
    except:
        return []


def analyze_patterns(examples: list) -> dict:
    """Analyze patterns across training examples"""
    analysis = {
        "total": len(examples),
        "outcomes": {},
        "common_objections": {},
        "effective_persuasion": [],
        "closing_success_rate": 0
    }
    
    for ex in examples:
        # Count outcomes
        outcome = ex.get("outcome", "unknown")
        analysis["outcomes"][outcome] = analysis["outcomes"].get(outcome, 0) + 1
        
        # Extract emotional cues
        cues = json.loads(ex.get("emotional_cues", "{}"))
        for obj in cues.get("objection_types", []):
            analysis["common_objections"][obj] = analysis["common_objections"].get(obj, 0) + 1
        
        # Track persuasion elements in successful outcomes
        if outcome == "booked":
            analysis["effective_persuasion"].extend(cues.get("persuasion_elements", []))
    
    # Calculate closing success rate
    if analysis["total"] > 0:
        booked = analysis["outcomes"].get("booked", 0)
        analysis["closing_success_rate"] = booked / analysis["total"]
    
    return analysis


# SQL to create training_data table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS training_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone TEXT,
    raw_text TEXT,
    scenario TEXT,
    outcome TEXT,
    takeaways JSONB,
    emotional_cues JSONB,
    agent TEXT DEFAULT 'sarah',
    learning_extracted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_scenario ON training_data(scenario);
CREATE INDEX IF NOT EXISTS idx_training_outcome ON training_data(outcome);
"""


# Export
__all__ = [
    "TRAINING_DATA_SCHEMA",
    "extract_emotional_cues",
    "extract_takeaways",
    "store_training_data",
    "get_training_examples",
    "analyze_patterns",
    "CREATE_TABLE_SQL"
]
