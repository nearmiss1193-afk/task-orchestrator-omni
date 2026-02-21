
import re
from collections import Counter

def check_duplicates():
    with open('deploy.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all function definitions
    matches = re.findall(r'def\s+(\w+)', content)
    
    counts = Counter(matches)
    dupes = {name: count for name, count in counts.items() if count > 1}
    
    if dupes:
        print(f"Total duplicates found: {len(dupes)}")
        for name, count in dupes.items():
            print(f"- {name}: {count} occurrences")
    else:
        print("No duplicate function names found.")

if __name__ == "__main__":
    check_duplicates()
