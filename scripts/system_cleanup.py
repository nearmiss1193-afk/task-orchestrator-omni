
import os
import shutil
import glob
import time

def cleanup_system():
    print("🧹 SOVEREIGN SYSTEM CLEANUP INITIATED...")
    
    root_dir = os.getcwd()
    
    # 1. Target Patterns (Safe Deletes)
    targets = [
        "**/*.temp",
        "**/*.log",
        "**/__pycache__",
        "**/*.pyc",
        "scripts/test_*.py", # Remove one-off test scripts
        "scripts/preview_*.py"
    ]
    
    files_deleted = 0
    space_freed = 0
    
    for pattern in targets:
        # Recursive globs for some patterns
        for filepath in glob.glob(os.path.join(root_dir, pattern), recursive=True):
            try:
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    space_freed += size
                    files_deleted += 1
                    print(f"   🗑️ Deleted: {os.path.basename(filepath)}")
                elif os.path.isdir(filepath):
                     shutil.rmtree(filepath)
                     print(f"   🗑️ Deleted Dir: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"   ⚠️ Failed: {filepath} ({e})")
                
    print(f"\n✨ CLEANUP COMPLETE.")
    print(f"   Files Removed: {files_deleted}")
    print(f"   Space Reclaimed: {space_freed / 1024:.2f} KB")
    
    # 2. Touch a 'clean_boot' marker
    with open("modules/ops/clean_boot.lock", "w") as f:
        f.write(str(int(time.time())))

if __name__ == "__main__":
    cleanup_system()
