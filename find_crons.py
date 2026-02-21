
import re

def find_crons():
    with open('deploy.py', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    crons = []
    for i, line in enumerate(lines):
        if 'schedule=modal.Cron' in line:
            # Look ahead for function name
            func_name = "unknown"
            for j in range(i+1, min(i+10, len(lines))):
                match = re.search(r'def\s+(\w+)', lines[j])
                if match:
                    func_name = match.group(1)
                    break
            crons.append({"line": i+1, "func": func_name, "def": line.strip()})
    
    print(f"Total Crons found: {len(crons)}")
    for c in crons:
        print(f"Line {c['line']}: {c['func']} -> {c['def']}")

if __name__ == "__main__":
    find_crons()
