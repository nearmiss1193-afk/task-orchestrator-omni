
import argparse
import glob
import json
import datetime
import os
import re

def learn_from_reports(targets, scan_pattern, limit, output_file, learn_mode):
    print(f"📘 PAGE BUILDER AUTO-LEARNING (v43.2)")
    
    file_pattern = os.path.join(targets, f"*{scan_pattern}*.md")
    files = sorted(glob.glob(file_pattern), key=os.path.getmtime, reverse=True)[:limit]
    
    print(f"Scanning {len(files)} recent reports in {targets}...")
    
    issues_count = {
        "optimize_images": 0,
        "relink_ctas": 0,
        "re_embed_widgets": 0
    }
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Heuristic Analysis
            if "Slow" in content or "(>3s)" in content:
                issues_count["optimize_images"] += 1
            if "Broken" in content or "Empty Link" in content:
                issues_count["relink_ctas"] += 1
            if "Widget Missing" in content:
                issues_count["re_embed_widgets"] += 1
                
    print("Detected Pattern Frequency:")
    print(json.dumps(issues_count, indent=2))
    
    # Generate Rules
    if learn_mode:
        rules = [k for k, v in issues_count.items() if v > 0]
        rule_set = {
            "updated": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "rules": rules
        }
        
        with open(output_file, "w") as f:
            json.dump(rule_set, f, indent=2)
            
        print(f"✅ Learned Rules saved to {output_file}")
        
       
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", required=True)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--learn", required=False) # Optional flag logic
    parser.add_argument("--output", required=False)
    args = parser.parse_args()
    
    learn_from_reports(args.scan, args.pattern, args.limit, args.output, args.learn)

if __name__ == "__main__":
    main()
