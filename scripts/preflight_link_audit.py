
import os
import sys

FORBIDDEN_STRINGS = [
    "localhost:3000",
    "127.0.0.1",
    "http://localhost"
]

IGNORE_DIRS = [".git", "node_modules", "venv", "__pycache__", ".vercel", ".next", "dist", "build"]
IGNORE_FILES = ["preflight_link_audit.py", "fix_html.py"]

def audit_directory(directory):
    violations = []
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
            
            if not file.endswith(('.html', '.py', '.js', '.json', '.md')):
                continue
                
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for forbidden in FORBIDDEN_STRINGS:
                        if forbidden in content:
                            violations.append(f"❌ VIOLATION: '{forbidden}' found in {path}")
            except Exception as e:
                # print(f"Could not read {path}: {e}")
                pass
    return violations

if __name__ == "__main__":
    print("🚀 Running Sovereign Sentinel Link Audit...")
    
    # Audit public, apps, and root
    violations = audit_directory("public")
    violations += audit_directory("apps")
    violations += audit_directory("scripts")
    
    # Audit root python files
    for file in os.listdir("."):
        if file.endswith(".py") and file not in IGNORE_FILES:
            path = os.path.abspath(file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for forbidden in FORBIDDEN_STRINGS:
                        if forbidden in content:
                            violations.append(f"❌ VIOLATION: '{forbidden}' found in {path}")
            except:
                pass

    if violations:
        print("\n🛑 DEPLOYMENT BLOCKED: Link Integrity Violations Found!")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print("\n✅ Internal Checks Passed: No 'Digital Ghosts' detected.")
        sys.exit(0)
