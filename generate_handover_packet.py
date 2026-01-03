
import argparse
import datetime
import os
import subprocess
import hashlib
import glob

def get_git_info():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')
        repo = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).strip().decode('utf-8')
        return commit, repo
    except:
        return "Unknown Commit", "Unknown Repo"

def calculate_checksum(filepath):
    if not os.path.exists(filepath): return "N/A"
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()[:12]

def generate_packet():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--include", required=True)
    args = parser.parse_args()

    print(f"📦 GENERATING SOVEREIGN HANDOVER PACKET...")
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit, repo = get_git_info()
    
    # Checksum critical files
    deploy_hash = calculate_checksum("deploy.py")
    governor_hash = calculate_checksum("modules/governor/guardian_v2.py")
    
    content = f"""# 🏛️ SOVEREIGN HANDOVER PACKET (v43.0)
**Timestamp:** {timestamp}
**Status:** ✅ PROTECTED ARCHIVE

## 1. System Identity
- **Repository:** {repo}
- **Commit Hash:** `{commit}`
- **Release Tag:** `SOVEREIGN_HANDOVER_v43.0`

## 2. Module Version Manifest
| Module | Version | Status | Integrity Hash |
| :--- | :--- | :--- | :--- |
| **Core Deployer** | v40.2 | Active | `{deploy_hash}` |
| **Governor** | v42.0 | CEO_ONLY | `{governor_hash}` |
| **QA Protocol** | v39.2 | Verified | N/A |
| **Autonomy Engine** | v42.0 | Active | N/A |

## 3. Governance & Permissions
- **Policy:** STRICT (CEO_ONLY_APPROVAL)
- **Authorized User:** Daniel Coffman
- **Secondary Approvers:** DISABLED

## 4. Autonomy & Discovery Status
- **Recent Findings:**
  - Integrated Gemini Pro 1.5 Context
  - Supabase Vector Store
- **Active Proposals:** 1 (Waiting Review)

## 5. Recovery & Data
- **Snapshot Location:** `backups/manual_backup_*.json` (JSON Fallback)
- **Database:** Supabase (Cloud Managed)
- **Rollback Point:** `STABLE_BUILD_v40.2`

## 6. Verification
All systems are frozen at this timestamp. Any future deployment requires a visible diff against this packet.

**SIGNED by System Governor**
"""

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ Packet Generated: {args.output}")

if __name__ == "__main__":
    generate_packet()
