import os
import shutil

path = r'C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\apps\portal\src\app\[slug]'
if os.path.exists(path):
    shutil.rmtree(path)
    print(f"✅ Deleted {path}")
else:
    print(f"❌ Path {path} not found")
