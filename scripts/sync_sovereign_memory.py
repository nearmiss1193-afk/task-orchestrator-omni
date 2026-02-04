"""
Sovereign Memory Sync Script
Syncs operational_memory.md to Supabase sovereign_memory table
Board approved: Grok, Gemini, ChatGPT unanimous (Feb 4, 2026)
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

def get_supabase() -> Client:
    """Get Supabase client with service role key."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_markdown_to_memory(filepath: str) -> list[dict]:
    """
    Parse operational_memory.md into structured memory entries.
    Returns list of {section, key, value} dicts.
    """
    entries = []
    current_section = "general"
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by headers
    lines = content.split("\n")
    
    for line in lines:
        # Detect section headers (## or ###)
        if line.startswith("## "):
            current_section = line.replace("## ", "").strip().lower()
            current_section = re.sub(r'[^\w\s]', '', current_section)
            current_section = current_section.replace(" ", "_")[:50]
        elif line.startswith("### "):
            subsection = line.replace("### ", "").strip().lower()
            subsection = re.sub(r'[^\w\s]', '', subsection)
            current_section = subsection.replace(" ", "_")[:50]
        
        # Detect key-value pairs (Key: Value or - **Key**: Value)
        kv_match = re.match(r'^[-*]?\s*\*?\*?(\w[\w\s]+)\*?\*?:\s*(.+)$', line.strip())
        if kv_match:
            key = kv_match.group(1).strip().lower().replace(" ", "_")[:100]
            value = kv_match.group(2).strip()
            if key and value:
                entries.append({
                    "section": current_section,
                    "key": key,
                    "value": value
                })
    
    return entries

def sync_memory_to_supabase(entries: list[dict], source: str = "sync_script"):
    """
    Upsert memory entries to Supabase.
    Uses ON CONFLICT to update existing entries.
    """
    supabase = get_supabase()
    
    success_count = 0
    error_count = 0
    
    for entry in entries:
        try:
            result = supabase.table("sovereign_memory").upsert({
                "section": entry["section"],
                "key": entry["key"],
                "value": entry["value"],
                "source": source,
                "last_updated": datetime.utcnow().isoformat()
            }, on_conflict="section,key").execute()
            
            if result.data:
                success_count += 1
            else:
                error_count += 1
                print(f"⚠️ No data returned for {entry['section']}/{entry['key']}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error upserting {entry['section']}/{entry['key']}: {e}")
    
    return success_count, error_count

def query_memory(section: str = None, key: str = None) -> list[dict]:
    """
    Query memory from Supabase.
    Modal webhooks use this to get operational context.
    """
    supabase = get_supabase()
    
    query = supabase.table("sovereign_memory").select("*")
    
    if section:
        query = query.eq("section", section)
    if key:
        query = query.eq("key", key)
    
    result = query.order("last_updated", desc=True).execute()
    return result.data if result.data else []

def get_all_memory() -> dict:
    """
    Get all memory as nested dict for easy access.
    Returns: {section: {key: value, ...}, ...}
    """
    entries = query_memory()
    memory = {}
    
    for entry in entries:
        section = entry.get("section", "general")
        key = entry.get("key", "unknown")
        value = entry.get("value", "")
        
        if section not in memory:
            memory[section] = {}
        memory[section][key] = value
    
    return memory

if __name__ == "__main__":
    import sys
    
    # Default path to operational memory
    memory_file = "knowledge_base/operational_memory.md"
    
    if len(sys.argv) > 1:
        memory_file = sys.argv[1]
    
    if not os.path.exists(memory_file):
        print(f"❌ File not found: {memory_file}")
        sys.exit(1)
    
    print(f"📖 Parsing {memory_file}...")
    entries = parse_markdown_to_memory(memory_file)
    print(f"📊 Found {len(entries)} memory entries")
    
    if entries:
        print("⬆️ Syncing to Supabase...")
        success, errors = sync_memory_to_supabase(entries)
        print(f"✅ Synced {success} entries, ❌ {errors} errors")
    else:
        print("⚠️ No entries found to sync")
    
    # Verify by querying back
    print("\n📥 Verifying by querying Supabase...")
    all_memory = get_all_memory()
    for section, keys in all_memory.items():
        print(f"  📁 {section}: {len(keys)} keys")
