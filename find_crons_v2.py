
import re

def find_crons():
    with open('deploy.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Match @app.function with schedule, followed by the def
    pattern = r'(@app\.function\(.*?schedule=modal\.Cron\(.*?\).*?\)\n(def\s+(\w+)))'
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"Total Crons found: {len(matches)}")
    for m in matches:
        print(f"Function: {m[2]}")
        print(f"Decorator: {m[0].split('def')[0].strip()}")
        print("-" * 20)

if __name__ == "__main__":
    find_crons()
