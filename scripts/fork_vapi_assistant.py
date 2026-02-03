
import os
import requests
import json

# Configuration
def load_env():
    # Candidates for .env.local
    
    # 1. Try python-dotenv if available (Standard)
    try:
        from dotenv import load_dotenv
        load_dotenv('.env.local')
        if os.environ.get("VAPI_PRIVATE_KEY"):
            print("✅ Loaded VAPI_PRIVATE_KEY from dotenv")
            return os.environ.get("VAPI_PRIVATE_KEY")
    except ImportError:
        pass

    # 2. Manual Search
    candidates = [
        os.path.abspath('.env.local'),
        os.path.abspath('apps/portal/.env.local'),
        os.path.abspath('../.env.local')
    ]
    print(f"🔍 Searching paths: {candidates}")
    
    for path in candidates:
        if os.path.exists(path):
            print(f"scan: {path} exists.")
            with open(path, 'r', encoding="utf-8") as f:
                for line in f:
                    if "VAPI_PRIVATE_KEY" in line:
                        print(f"found key in {path}")
                        try:
                            return line.strip().split('=', 1)[1].strip('"').strip("'")
                        except:
                            pass
    return None

VAPI_PRIVATE_KEY = os.environ.get("VAPI_PRIVATE_KEY") or load_env()
VAPI_BASE_URL = "https://api.vapi.ai"

# Current "Master" Assistant ID (Office Manager)
SOURCE_ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

# Path to update in the NEW Shard
SHARD_DIR = os.path.join(os.path.dirname(os.getcwd()), "empire-unified-shard-2") 
TARGET_FILE = os.path.join(SHARD_DIR, "vapi_id.txt")
TARGET_HTML_DIR = os.path.join(SHARD_DIR, "apps", "portal", "public", "landing")

def fork_assistant():
    if not VAPI_PRIVATE_KEY:
        print("❌ VAPI_PRIVATE_KEY not found in environment.")
        return

    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

    print(f"🧬 Forking Assistant {SOURCE_ASSISTANT_ID}...")

    # 1. Get Source Config
    try:
        res = requests.get(f"{VAPI_BASE_URL}/assistant/{SOURCE_ASSISTANT_ID}", headers=headers)
        if res.status_code != 200:
            print(f"❌ Failed to fetch source assistant: {res.text}")
            return
        source_data = res.json()
    except Exception as e:
        print(f"❌ Error fetching source: {e}")
        return

    # 2. Create New Config (Clone)
    new_data = source_data.copy()
    if "id" in new_data: del new_data["id"] 
    if "orgId" in new_data: del new_data["orgId"]
    if "createdAt" in new_data: del new_data["createdAt"]
    if "updatedAt" in new_data: del new_data["updatedAt"]
    
    new_data["name"] = f"{source_data.get('name', 'Office Manager')} (Shard 2)"
    
    # 3. Create New Assistant
    try:
        res = requests.post(f"{VAPI_BASE_URL}/assistant", headers=headers, json=new_data)
        if res.status_code != 201:
            print(f"❌ Failed to create fork: {res.text}")
            return
        new_assistant = res.json()
        new_id = new_assistant["id"]
        print(f"✅ Created New Assistant: {new_id} ({new_data['name']})")
    except Exception as e:
        print(f"❌ Error creating fork: {e}")
        return

    # 4. Update SHARD 2 Files
    if not os.path.exists(SHARD_DIR):
        print(f"⚠️ Shard directory {SHARD_DIR} not found. Clone system first!")
        return

    # Update vapi_id.txt
    if os.path.exists(os.path.dirname(TARGET_FILE)):
        with open(TARGET_FILE, "w") as f:
            f.write(new_id)
        print(f"✅ Updated {TARGET_FILE}")

    # Update Landing Pages in Shard 2
    import glob
    html_files = glob.glob(os.path.join(TARGET_HTML_DIR, "*.html"))
    count = 0
    for file in html_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace old ID with new ID
        new_content = content.replace(SOURCE_ASSISTANT_ID, new_id)
        
        if new_content != content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1
    
    print(f"✅ Updated {count} Landing Pages in Shard 2 with New Vapi ID.")

if __name__ == "__main__":
    fork_assistant()
