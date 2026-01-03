
import os
import shutil
import json
import re

SOURCE_DIR = os.getcwd() # e.g. .../empire-unified
PARENT_DIR = os.path.dirname(SOURCE_DIR)
TARGET_DIR_NAME = "empire-unified-shard-2"
TARGET_DIR = os.path.join(PARENT_DIR, TARGET_DIR_NAME)

IGNORE_PATTERNS = shutil.ignore_patterns(
    "node_modules", 
    ".next", 
    ".git", 
    "dist", 
    "build", 
    "__pycache__", 
    "*.log", 
    "logs", 
    "scratch",
    "brain", # Artifacts stay in the "Brain" workspace, not needed in shard code
    TARGET_DIR_NAME # Avoid recursive copy if target is inside source
)

def clone_system():
    print(f"🧬 Cloning System...")
    print(f"   Source: {SOURCE_DIR}")
    print(f"   Target: {TARGET_DIR}")
    
    if os.path.exists(TARGET_DIR):
        print(f"⚠️ Target directory exists. Removing for clean clone...")
        shutil.rmtree(TARGET_DIR)
        
    try:
        shutil.copytree(SOURCE_DIR, TARGET_DIR, ignore=IGNORE_PATTERNS)
        print(f"✅ Filesystem Cloned.")
    except Exception as e:
        print(f"❌ Clone Failed: {e}")
        return

    # Post-Clone Configuration
    
    # 1. Update Port in package.json (Next.js)
    pkg_path = os.path.join(TARGET_DIR, "apps", "portal", "package.json")
    if os.path.exists(pkg_path):
        with open(pkg_path, "r") as f:
            data = json.load(f)
        
        # Modify dev script: "next dev" -> "next dev -p 3001"
        if "scripts" in data and "dev" in data["scripts"]:
            data["scripts"]["dev"] = "next dev -p 3001"
            print("✅ Port updated to 3001 in package.json")
            
        with open(pkg_path, "w") as f:
            json.dump(data, f, indent=2)

    # 2. Reset Database
    db_path = os.path.join(TARGET_DIR, "db", "clients.json")
    if os.path.exists(db_path):
        with open(db_path, "w") as f:
            json.dump([], f)
        print("✅ Client Database Reset (Clean Slate for Shard 2)")

    # 3. Create 'SHARD_ID' file
    with open(os.path.join(TARGET_DIR, "SHARD_ID"), "w") as f:
        f.write("SHARD-2")

    print(f"🎉 Clone Complete! New System ready at: {TARGET_DIR}")
    print("   Run 'npm install' and 'npm run dev' in the new folder to start.")

if __name__ == "__main__":
    clone_system()
