import os
import zipfile

def zip_project(output_filename):
    exclude_dirs = {'.git', 'node_modules', 'logs', '__pycache__', '.vercel', '.pytest_cache'}
    exclude_exts = {'.zip', '.exe', '.bin', '.pyc', '.png', '.jpg', '.webp', '.ico'} # Excluding images as they are "binaries" and might bloat the zip

    print(f"📦 Starting zip: {output_filename}")
    
    # We'll use the current directory
    root_dir = os.getcwd()
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Prune exclude_dirs
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in exclude_exts):
                    continue
                
                file_path = os.path.join(root, file)
                # Ensure we don't zip the zip file itself if it's in the same dir
                if file == output_filename:
                    continue
                
                arcname = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, arcname)
                # print(f"Added: {arcname}")

    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"✅ ZIP COMPLETE - {output_filename} - FILE SIZE: {size_mb:.2f} MB")

if __name__ == "__main__":
    zip_project("aiserviceco-full-project-v1.zip")

token: `sov-audit-2026-ghost`
