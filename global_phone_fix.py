import os
import re

# TARGETS
ROOT_DIR = r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified"
EXCLUDE_DIRS = ['backups', '.git', '.vercel', 'node_modules', '__pycache__']

OLD_NUMBERS = [
    r"407-289-1784",
    r"\(407\) 289-1784",
    r"4072891784",
    r"1-407-289-1784",
    r"\+1 407-289-1784",
    r"\+1 \(407\) 289-1784"
]

NEW_DISPLAY = "(352) 758-5336"
NEW_LINK = "+13527585336"

def global_replace():
    print(f"🚀 Starting GLOBAL Identity Transition to {NEW_DISPLAY}")
    
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith(('.html', '.py', '.js', '.css', '.tsx', '.ts', '.md', '.json')):
                if file == 'global_phone_fix.py': continue
                
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    original = content
                    
                    # Replace Variations
                    for pattern in OLD_NUMBERS:
                        # If it's in a tel: link
                        content = re.sub(f"tel:{pattern}", f"tel:{NEW_LINK}", content)
                        # Regular display
                        content = re.sub(pattern, NEW_DISPLAY, content)
                    
                    if content != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Updated: {path}")
                        count += 1
                except Exception as e:
                    print(f"❌ Error in {path}: {e}")

    print(f"\n✨ Done. Updated {count} files.")

if __name__ == "__main__":
    global_replace()
