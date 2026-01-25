import re

def strip_functions():
    with open("deploy.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to remove entire function blocks including decorators
    # Matches @app.function... down to the next @app.function or EOF, checking if it defines the target function
    # Wait, simpler: Remove by name.
    
    # Remove api_read_file
    # Logic: Find @app.function... def api_read_file... end or next decorator
    # This is hard with regex.
    # Let's use string partitioning of specific chunks I see in the file.
    
    # 1. Remove api_read_file
    # I saw it around line 1159 in grep.
    # I'll replace the text.
    
    # Pattern for api_read_file
    pattern_read = r'@app\.function\(image=image, secrets=\[VAULT\]\)\s*@modal\.fastapi_endpoint\(method="GET"\)\s*def api_read_file\(path: str\):.*?return \{"error": str\(e\)\}'
    # This assumes we match the body. 
    # Better: Read lines and filter.
    
    lines = content.split('\n')
    new_lines = []
    skip = False
    
    targets = ["def api_read_file", "def api_dashboard_stats", "def fastapi_app"]
    
    for i, line in enumerate(lines):
        # Look ahead for decorators if we are about to hit a target
        # Actually, simpler: identify ranges manually? No.
        
        # Heuristic: If line starts with @app.function, check next few lines for target def name.
        if line.strip().startswith("@app.function"):
            # Check next 5 lines
            is_target = False
            for j in range(1, 10):
                if i+j < len(lines):
                    if any(t in lines[i+j] for t in targets):
                        is_target = True
                        break
            if is_target:
                skip = True
                print(f"Skipping block starting at {i}")
        
        if skip:
            # When to stop skipping?
            # When we hit next @app.function OR if __name__ OR huge whitespace break?
            # Or simplified: checking if current line is next function?
            if line.strip().startswith("@app.function") and not any(t in "".join(lines[i:i+10]) for t in targets):
                skip = False
                # But current line is the start of next function, so don't append yet?
                # Actually, `skip` flag logic needs to be careful.
                # If skipping, and we see @app.function (new one), we stop skipping AND append current line.
                new_lines.append(line)
            # What if we hit if __name__?
            elif line.startswith("if __name__"):
                skip = False
                new_lines.append(line)
            # Continue skipping
        else:
            new_lines.append(line)
            
    with open("deploy.py", "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines))
    print("Done stripping.")

if __name__ == "__main__":
    strip_functions()
