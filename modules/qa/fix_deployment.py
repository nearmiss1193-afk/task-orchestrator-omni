
import os
import shutil

def fix_deployment():
    print("🔧 Starting Deployment Fix...")
    
    source_dir = "apps/portal/public/landing"
    public_dir = "public"
    
    # 1. Check Source
    if not os.path.exists(source_dir):
        print(f"❌ ERROR: Source directory '{source_dir}' NOT FOUND.")
        return
        
    # 2. Check/Make Public
    if not os.path.exists(public_dir):
        print(f"   Creating '{public_dir}' directory...")
        os.makedirs(public_dir)
    else:
        print(f"   '{public_dir}' directory exists.")
        
    # 3. Copy Files
    files = os.listdir(source_dir)
    print(f"   Found {len(files)} files in source.")
    
    for f in files:
        src = os.path.join(source_dir, f)
        dst = os.path.join(public_dir, f)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            # print(f"   Copied {f}")
            
    # 4. Final Verify
    if os.path.exists(os.path.join(public_dir, "index.html")):
        print("✅ SUCCESS: public/index.html exists.")
    else:
        print("❌ FAIL: public/index.html MISSING after copy.")

if __name__ == "__main__":
    fix_deployment()
