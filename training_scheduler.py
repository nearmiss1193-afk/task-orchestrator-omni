"""
TRAINING SCHEDULER
Manages background agent training sessions.
Ensures agents are always learning when idle.
"""

import os
import json
import schedule
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TRAINING_LOG = Path("training_log.json")
KNOWLEDGE_DIR = Path("knowledge_base")

# Training schedule (can be adjusted)
TRAINING_SCHEDULE = {
    "ghl": {"frequency": "daily", "time": "02:00"},      # GHL at 2 AM
    "vapi": {"frequency": "daily", "time": "03:00"},     # Vapi at 3 AM
    "twilio": {"frequency": "weekly", "time": "04:00"},  # Twilio weekly
    "resend": {"frequency": "weekly", "time": "04:30"},  # Resend weekly
    "supabase": {"frequency": "daily", "time": "05:00"}, # Supabase at 5 AM
    "openai": {"frequency": "daily", "time": "06:00"},   # OpenAI at 6 AM
}

# Priority learning topics per tool
PRIORITY_TOPICS = {
    "ghl": [
        "workflows/webhook-trigger",
        "workflows/sms-actions",
        "workflows/email-actions",
        "contacts/create-update",
        "opportunities/pipeline",
        "conversations/messages"
    ],
    "vapi": [
        "assistants/update",
        "calls/create-outbound",
        "phone-numbers/manage",
        "webhooks/call-events",
        "transcripts/get"
    ],
    "twilio": [
        "a2p-10dlc/registration",
        "messaging-services/setup",
        "sms/send",
        "phone-numbers/capabilities"
    ]
}

def log_training(tool: str, status: str, details: dict = None):
    """Log training session"""
    log = []
    if TRAINING_LOG.exists():
        with open(TRAINING_LOG) as f:
            log = json.load(f)
    
    log.append({
        "timestamp": datetime.now().isoformat(),
        "tool": tool,
        "status": status,
        "details": details or {}
    })
    
    # Keep last 1000 entries
    log = log[-1000:]
    
    with open(TRAINING_LOG, "w") as f:
        json.dump(log, f, indent=2)

def run_training(tool: str):
    """Execute training for a tool"""
    print(f"[TRAINING] Starting {tool} training session...")
    try:
        from knowledge_crawler import run_learning_session
        result = run_learning_session([tool])
        log_training(tool, "success", {"files_created": len(result.get(tool, []))})
        print(f"[TRAINING] {tool} complete!")
    except Exception as e:
        log_training(tool, "error", {"error": str(e)})
        print(f"[TRAINING] {tool} failed: {e}")

def get_training_status() -> dict:
    """Get current training status"""
    status = {
        "last_runs": {},
        "knowledge_files": {},
        "schedule": TRAINING_SCHEDULE
    }
    
    if TRAINING_LOG.exists():
        with open(TRAINING_LOG) as f:
            log = json.load(f)
            for entry in reversed(log):
                if entry["tool"] not in status["last_runs"]:
                    status["last_runs"][entry["tool"]] = entry
    
    for tool in TRAINING_SCHEDULE:
        tool_dir = KNOWLEDGE_DIR / tool
        if tool_dir.exists():
            status["knowledge_files"][tool] = len(list(tool_dir.glob("*.json")))
        else:
            status["knowledge_files"][tool] = 0
    
    return status

def setup_schedule():
    """Setup automated training schedule"""
    for tool, config in TRAINING_SCHEDULE.items():
        if config["frequency"] == "daily":
            schedule.every().day.at(config["time"]).do(run_training, tool)
        elif config["frequency"] == "weekly":
            schedule.every().monday.at(config["time"]).do(run_training, tool)
    
    print("[SCHEDULER] Training schedule configured:")
    for tool, config in TRAINING_SCHEDULE.items():
        print(f"  - {tool}: {config['frequency']} at {config['time']}")

def run_scheduler():
    """Run the training scheduler loop"""
    setup_schedule()
    print("\n[SCHEDULER] Starting training scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            status = get_training_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "now":
            # Run immediate training for all
            for tool in TRAINING_SCHEDULE:
                run_training(tool)
        elif sys.argv[1] in TRAINING_SCHEDULE:
            run_training(sys.argv[1])
    else:
        run_scheduler()
