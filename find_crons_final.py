
import re

def find_crons():
    with open('deploy.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Match @app.function with schedule, followed by the def
    pattern = r'@app\.function\(.*?schedule=modal\.Cron\(.*?\).*?\)\s+def\s+(\w+)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    count = 0
    for m in matches:
        count += 1
        print(f"Cron {count}: {m.group(1)}")
        # Print first line of the decorator to see line number roughly
        # Actually just print the whole match
        # print(m.group(0))
        # print("-" * 20)

if __name__ == "__main__":
    find_crons()
