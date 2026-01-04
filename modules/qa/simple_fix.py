
import os

def brute_force_copy():
    print("🔧 Starting Brute Force Copy (Binary Mode)...")
    
    src_dir = "apps/portal/public/landing"
    dst_dir = "public"
    
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    for filename in os.listdir(src_dir):
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, filename)
        
        if os.path.isfile(src_path):
            try:
                with open(src_path, 'rb') as f_in:
                    content = f_in.read()
                    with open(dst_path, 'wb') as f_out:
                        f_out.write(content)
                print(f"   [OK] {filename}")
            except Exception as e:
                print(f"   [ERR] {filename}: {e}")

    if os.path.exists(os.path.join(dst_dir, "index.html")):
        print("\n✅ VERIFICATION PASSED: public/index.html exists.")
    else:
        print("\n❌ VERIFICATION FAILED.")

if __name__ == "__main__":
    brute_force_copy()
