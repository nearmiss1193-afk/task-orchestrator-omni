
import subprocess
import time

def run_batch():
    # Read Existing
    try:
        with open('site_targets.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except:
        urls = []
        
    # Add Next Campaign
    next_campaign = "https://hvac.aiserviceco.com"
    if next_campaign not in urls:
        urls.append(next_campaign)
        
    print(f"[STARTING BATCH REPAIR] for {len(urls)} SITES...")
    
    for url in urls:
        print(f"\nTarget: {url}")
        subprocess.run(f"python pagebuilder_selfrepair.py --rules pagebuilder_rules.json --site {url}", shell=True)
        time.sleep(1)
        
    print("\n[BATCH COMPLETE].")

if __name__ == "__main__":
    run_batch()
