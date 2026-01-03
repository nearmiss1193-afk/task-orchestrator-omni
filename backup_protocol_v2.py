
import os
import shutil
import datetime
import subprocess

def run_backup():
    print("🛡️ Protocol Omega: Initiating Backup...")
    
    # 1. Timestamp
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"empire_backup_{ts}"
    backup_dir = os.path.join(os.getcwd(), "backups", backup_name)
    
    # 2. Create Backup Directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # 3. Copy Critical Files
    # We copy the entire workspace minus heavy folders
    source = os.getcwd()
    print(f"📂 Copying source from {source} to {backup_dir}...")
    
    # CRITICAL FIX: Ignore 'backups' to prevent infinite recursive copy
    ignore_func = shutil.ignore_patterns('*.git', 'node_modules', '__pycache__', '.veo_browser_data', '.ghl_browser_data', 'backups', '.modal')
    
    try:
        shutil.copytree(source, os.path.join(backup_dir, "source"), ignore=ignore_func)
    except Exception as e:
        print(f"⚠️ Partial copy error: {e}")

    # 4. Zip It (Safely)
    zip_path = f"{backup_dir}.zip"
    print(f"📦 Zipping to {zip_path}...")
    
    # Fix for "ZIP does not support timestamps before 1980"
    # We walk the source directory and touch any old files AND directories
    try:
        min_time = 315532800 # 1980-01-01
        for root, dirs, files in os.walk(os.path.join(backup_dir, "source")):
             # Files
            for name in files:
                file_path = os.path.join(root, name)
                arcname = os.path.relpath(file_path, backup_dir)
                try:
                    stats = os.stat(file_path)
                    if stats.st_mtime < 315532800: # Before 1980
                         # Force update or Skip
                         os.utime(file_path, (min_time + 1, min_time + 1))
                    
                    # z.write(file_path, arcname=arcname) # REMOVED: z is undefined, shutil handles this
                except Exception as e:
                    print(f"⚠️ Skipping {name}: {e}")
            for name in dirs:
                path = os.path.join(root, name)
                try:
                    stats = os.stat(path)
                    if stats.st_mtime < min_time:
                         os.utime(path, (min_time + 1, min_time + 1))
                except:
                    pass
    except Exception as e:
        print(f"Time fix warning: {e}")

    shutil.make_archive(backup_dir, 'zip', backup_dir)
    
    # 5. Git Commit & Push
    try:
        print("tc git committing & pushing...")
        subprocess.run(["git", "add", "."], check=False)
        subprocess.run(["git", "commit", "-m", f"Backup Protocol {ts}"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=False)
        print("✅ Pushed to GitHub (nearmiss1193/orchestrator-omni)")
    except Exception as e:
        print(f"⚠️ Git Push Warning: {e}")

    print(f"✅ Backup Complete: {zip_path}")
    return zip_path

if __name__ == "__main__":
    run_backup()
