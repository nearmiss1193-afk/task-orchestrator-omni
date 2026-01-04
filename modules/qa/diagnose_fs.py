
import os
import shutil
import sys

def diagnose_and_fix():
    print("🩺 STARTING FS DIAGNOSIS")
    
    root = os.getcwd()
    print(f"   Root: {root}")
    
    target_dir = "public"
    source_file = "apps/portal/public/landing/index.html"
    
    # 1. Inspect 'public'
    if os.path.exists(target_dir):
        if os.path.isfile(target_dir):
            print(f"⚠️ ALERT: '{target_dir}' exists but is a FILE. Deleting...")
            try:
                os.remove(target_dir)
                print("   Deleted file.")
            except Exception as e:
                print(f"❌ Failed to delete file: {e}")
                return
        elif os.path.isdir(target_dir):
            print(f"   '{target_dir}' is a valid DIRECTORY.")
        else:
            print(f"   '{target_dir}' is weird (symlink?).")
    else:
        print(f"   '{target_dir}' does NOT exist.")
        
    # 2. Ensure Dir
    if not os.path.exists(target_dir):
        print(f"   Creating '{target_dir}'...")
        os.makedirs(target_dir)
        
    # 3. Check Source
    if not os.path.exists(source_file):
        print(f"❌ ERROR: Source '{source_file}' NOT FOUND.")
        # List parent dir to debug
        parent = os.path.dirname(source_file)
        if os.path.exists(parent):
            print(f"   Listing {parent}: {os.listdir(parent)}")
        return
        
    # 4. Copy
    dest = os.path.join(target_dir, "index.html")
    print(f"   Copying to {dest}...")
    try:
        shutil.copy2(source_file, dest)
        print("✅ COPY SUCCESS.")
    except Exception as e:
        print(f"❌ COPY FAILED: {e}")

if __name__ == "__main__":
    diagnose_and_fix()
