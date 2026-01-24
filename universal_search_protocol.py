import os
import sys
import fnmatch

# Configuration
SEARCH_ROOT_OFFSET = "../../"  # Go up two levels from playground/empire-unified to 'antigravity'
TARGET_DIRECTORIES = ["scratch", "playground", "brain"]
SAFE_EXTENSIONS = [".env", ".txt", ".md", ".json", ".py", ".js", ".html"]
IGNORE_DIRS = ["node_modules", ".git", "__pycache__", "venv", ".modal"]

def find_credentials(search_term):
    """
    Searches for a specific term across the entire Antigravity workspace.
    Targeting specific directories to avoid massive scans of unrelated data.
    """
    base_path = os.path.abspath(os.path.join(os.getcwd(), SEARCH_ROOT_OFFSET))
    print(f"🔍 Starting Universal Search Protocol (USP)")
    print(f"📂 Root: {base_path}")
    print(f"🎯 Target: '{search_term}'")
    
    found_count = 0
    
    for target_dir in TARGET_DIRECTORIES:
        search_path = os.path.join(base_path, target_dir)
        if not os.path.exists(search_path):
            print(f"⚠️  Skipping {target_dir} (Not found)")
            continue
            
        print(f"   Scanning {target_dir}...")
        
        for root, dirs, files in os.walk(search_path):
            # Filtering directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                # Filter extensions
                if not any(file.endswith(ext) for ext in SAFE_EXTENSIONS):
                    continue
                    
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if search_term in line:
                                # Found a match
                                found_count += 1
                                relative_path = os.path.relpath(file_path, base_path)
                                print(f"\n✅ FOUND in {relative_path}:{i+1}")
                                print(f"   {line.strip()[:100]}...") # Print preview, truncated
                except Exception as e:
                    # Silently fail on read errors (permissions, locks)
                    pass

    if found_count == 0:
        print("\n❌ No matches found in any target sector.")
    else:
        print(f"\n✨ Search Complete. Found {found_count} instances.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python universal_search_protocol.py <search_term>")
        sys.exit(1)
    
    term = sys.argv[1]
    find_credentials(term)
