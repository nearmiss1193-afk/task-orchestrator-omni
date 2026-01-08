"""
AUTONOMOUS KNOWLEDGE CRAWLER
Continuously learns from tool documentation, forums, and updates.
Runs in background to build agent intelligence without human intervention.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path("knowledge_base")
KNOWLEDGE_DIR.mkdir(exist_ok=True)

# Core tools to master
KNOWLEDGE_SOURCES = {
    "ghl": {
        "docs": "https://highlevel.stoplight.io/docs/integrations",
        "api": "https://services.leadconnectorhq.com",
        "topics": ["workflows", "webhooks", "contacts", "sms", "email", "pipelines", "opportunities"]
    },
    "vapi": {
        "docs": "https://docs.vapi.ai",
        "api": "https://api.vapi.ai",
        "topics": ["assistants", "calls", "phone-numbers", "transcripts", "webhooks", "voice"]
    },
    "twilio": {
        "docs": "https://www.twilio.com/docs",
        "api": "https://api.twilio.com",
        "topics": ["sms", "voice", "a2p-10dlc", "messaging-services", "phone-numbers"]
    },
    "resend": {
        "docs": "https://resend.com/docs",
        "api": "https://api.resend.com",
        "topics": ["emails", "domains", "audiences", "broadcasts"]
    },
    "supabase": {
        "docs": "https://supabase.com/docs",
        "api": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
        "topics": ["database", "auth", "storage", "edge-functions", "realtime"]
    },
    "openai": {
        "docs": "https://platform.openai.com/docs",
        "api": "https://api.openai.com/v1",
        "topics": ["chat", "assistants", "embeddings", "fine-tuning", "function-calling"]
    }
}

def fetch_docs(url: str) -> dict:
    """Fetch and parse documentation page"""
    try:
        headers = {"User-Agent": "EmpireKnowledgeCrawler/1.0"}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return {"status": "success", "content": response.text[:50000], "url": url}
        return {"status": "error", "code": response.status_code, "url": url}
    except Exception as e:
        return {"status": "error", "message": str(e), "url": url}

def save_knowledge(tool: str, topic: str, content: dict):
    """Save learned knowledge to local knowledge base"""
    tool_dir = KNOWLEDGE_DIR / tool
    tool_dir.mkdir(exist_ok=True)
    
    filename = f"{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(tool_dir / filename, "w") as f:
        json.dump({
            "tool": tool,
            "topic": topic,
            "learned_at": datetime.now().isoformat(),
            "content": content
        }, f, indent=2)
    print(f"[LEARNED] {tool}/{topic}")

def get_learning_status() -> dict:
    """Check what has been learned so far"""
    status = {}
    for tool in KNOWLEDGE_SOURCES:
        tool_dir = KNOWLEDGE_DIR / tool
        if tool_dir.exists():
            status[tool] = list(tool_dir.glob("*.json"))
        else:
            status[tool] = []
    return status

def run_learning_session(tools: list = None):
    """Run a learning session for specified tools or all tools"""
    if tools is None:
        tools = list(KNOWLEDGE_SOURCES.keys())
    
    print(f"\n{'='*60}")
    print(f"KNOWLEDGE CRAWLER - Learning Session")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Tools: {', '.join(tools)}")
    print(f"{'='*60}\n")
    
    for tool in tools:
        if tool not in KNOWLEDGE_SOURCES:
            print(f"[SKIP] Unknown tool: {tool}")
            continue
            
        source = KNOWLEDGE_SOURCES[tool]
        print(f"\n[LEARNING] {tool.upper()}")
        
        # Fetch main docs
        docs_result = fetch_docs(source["docs"])
        if docs_result["status"] == "success":
            save_knowledge(tool, "main_docs", docs_result)
        
        # Could add more sophisticated parsing/learning here
        
    print(f"\n[COMPLETE] Learning session finished")
    return get_learning_status()

if __name__ == "__main__":
    import sys
    tools = sys.argv[1:] if len(sys.argv) > 1 else None
    status = run_learning_session(tools)
    print(f"\nKnowledge Status: {json.dumps({k: len(v) for k, v in status.items()}, indent=2)}")
