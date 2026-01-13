"""
📦 SYSTEM CONFIG BACKUP
=======================
Exports all system configurations to local backup files.
Run weekly or before major changes.

Backs up:
- Vapi assistants and phone numbers
- GHL location settings
- Supabase schema snapshot
- Current .env (sanitized)
- Agent learnings from database
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# === CONFIG ===
BACKUP_DIR = Path("backups")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# API Keys
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
GHL_KEY = os.getenv("GHL_API_KEY")
GHL_LOCATION = os.getenv("GHL_LOCATION_ID")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def ensure_backup_dir():
    """Create backup directory if needed."""
    BACKUP_DIR.mkdir(exist_ok=True)
    return BACKUP_DIR / TIMESTAMP
    

def backup_vapi_assistants(backup_path: Path):
    """Export all Vapi assistants."""
    if not VAPI_KEY:
        log("⚠️ No VAPI_KEY - skipping Vapi backup")
        return
    
    log("📞 Backing up Vapi assistants...")
    
    try:
        resp = requests.get(
            "https://api.vapi.ai/assistant",
            headers={"Authorization": f"Bearer {VAPI_KEY}"},
            timeout=30
        )
        
        if resp.status_code == 200:
            assistants = resp.json()
            with open(backup_path / "vapi_assistants.json", "w") as f:
                json.dump(assistants, f, indent=2)
            log(f"   ✅ Saved {len(assistants)} assistants")
        else:
            log(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        log(f"   ❌ Error: {e}")


def backup_vapi_phones(backup_path: Path):
    """Export Vapi phone numbers."""
    if not VAPI_KEY:
        return
    
    log("📱 Backing up Vapi phone numbers...")
    
    try:
        resp = requests.get(
            "https://api.vapi.ai/phone-number",
            headers={"Authorization": f"Bearer {VAPI_KEY}"},
            timeout=30
        )
        
        if resp.status_code == 200:
            phones = resp.json()
            with open(backup_path / "vapi_phones.json", "w") as f:
                json.dump(phones, f, indent=2)
            log(f"   ✅ Saved {len(phones)} phone numbers")
    except Exception as e:
        log(f"   ❌ Error: {e}")


def backup_ghl_location(backup_path: Path):
    """Export GHL location settings."""
    if not GHL_KEY or not GHL_LOCATION:
        log("⚠️ No GHL credentials - skipping GHL backup")
        return
    
    log("🏢 Backing up GHL location...")
    
    try:
        resp = requests.get(
            f"https://services.leadconnectorhq.com/locations/{GHL_LOCATION}",
            headers={
                "Authorization": f"Bearer {GHL_KEY}",
                "Version": "2021-07-28"
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            location = resp.json()
            with open(backup_path / "ghl_location.json", "w") as f:
                json.dump(location, f, indent=2)
            log("   ✅ Saved location settings")
        else:
            log(f"   ⚠️ GHL returned {resp.status_code}")
    except Exception as e:
        log(f"   ❌ Error: {e}")


def backup_supabase_data(backup_path: Path):
    """Export key Supabase tables."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        log("⚠️ No Supabase credentials - skipping")
        return
    
    log("🗄️ Backing up Supabase data...")
    
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Tables to backup
        tables = [
            ("agent_learnings", 1000),
            ("error_logs", 500),
            ("system_logs", 200),
        ]
        
        for table_name, limit in tables:
            try:
                result = client.table(table_name).select("*").limit(limit).execute()
                with open(backup_path / f"supabase_{table_name}.json", "w") as f:
                    json.dump(result.data, f, indent=2)
                log(f"   ✅ {table_name}: {len(result.data)} rows")
            except Exception as e:
                log(f"   ⚠️ {table_name}: {e}")
                
    except Exception as e:
        log(f"   ❌ Error: {e}")


def backup_env_sanitized(backup_path: Path):
    """Export .env with values masked."""
    log("🔐 Backing up .env (sanitized)...")
    
    env_path = Path(".env")
    if not env_path.exists():
        log("   ⚠️ No .env file found")
        return
    
    lines = []
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                # Mask sensitive values
                if any(x in key.upper() for x in ["KEY", "SECRET", "TOKEN", "PASSWORD"]):
                    masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                    lines.append(f"{key}={masked}")
                else:
                    lines.append(line)
            else:
                lines.append(line)
    
    with open(backup_path / "env_sanitized.txt", "w") as f:
        f.write("\n".join(lines))
    log("   ✅ Saved sanitized .env")


def backup_knowledge_base(backup_path: Path):
    """Copy knowledge base files."""
    log("📚 Backing up knowledge base...")
    
    kb_dir = Path("knowledge_base")
    if not kb_dir.exists():
        return
    
    kb_backup = backup_path / "knowledge_base"
    kb_backup.mkdir(exist_ok=True)
    
    count = 0
    for file in kb_dir.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        with open(kb_backup / file.name, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1
    
    log(f"   ✅ Saved {count} knowledge docs")


def create_manifest(backup_path: Path):
    """Create backup manifest."""
    files = list(backup_path.rglob("*"))
    
    manifest = {
        "timestamp": TIMESTAMP,
        "files": [str(f.relative_to(backup_path)) for f in files if f.is_file()],
        "total_files": len([f for f in files if f.is_file()]),
        "created_at": datetime.now().isoformat()
    }
    
    with open(backup_path / "MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)


def run_backup():
    """Run complete backup."""
    print("=" * 60)
    print("📦 SYSTEM CONFIG BACKUP")
    print("=" * 60)
    print(f"Timestamp: {TIMESTAMP}")
    print()
    
    backup_path = ensure_backup_dir()
    backup_path.mkdir(exist_ok=True)
    
    # Run all backups
    backup_vapi_assistants(backup_path)
    backup_vapi_phones(backup_path)
    backup_ghl_location(backup_path)
    backup_supabase_data(backup_path)
    backup_env_sanitized(backup_path)
    backup_knowledge_base(backup_path)
    
    # Create manifest
    create_manifest(backup_path)
    
    print()
    print("=" * 60)
    print(f"✅ BACKUP COMPLETE: {backup_path}")
    print("=" * 60)
    
    return backup_path


if __name__ == "__main__":
    run_backup()
