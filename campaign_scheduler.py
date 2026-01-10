"""
CAMPAIGN SCHEDULER - 100 OUTREACH/DAY GOAL
==========================================
Runs campaign every 2 minutes until 100 total outreach achieved.
"""
import os
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Configuration
INTERVAL_SECONDS = 120  # 2 minutes
DAILY_GOAL = 100  # Total outreach (GHL pushes + Calls)
PROGRESS_FILE = "campaign_progress.json"

def load_progress():
    """Load today's progress."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                # Reset if it's a new day
                if data.get('date') != datetime.now().strftime('%Y-%m-%d'):
                    return {'date': datetime.now().strftime('%Y-%m-%d'), 'count': 0, 'batches': 0}
                return data
        except:
            pass
    return {'date': datetime.now().strftime('%Y-%m-%d'), 'count': 0, 'batches': 0}

def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def run_campaign_batch():
    """Run one campaign batch and return success count."""
    try:
        result = subprocess.run(
            ['python', 'campaign_v2.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 min max per batch
        )
        
        # Parse log to count successes
        log_path = 'campaign_v2_logs.txt'
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()
                # Count recent "GHL accepted" entries
                recent_lines = lines[-20:]  # Last 20 lines
                count = sum(1 for line in recent_lines if 'GHL accepted' in line)
                return count
        return 0
    except Exception as e:
        print(f"⚠️ Batch error: {e}")
        return 0

def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      CAMPAIGN SCHEDULER - 100 OUTREACH GOAL             ║
║      Run Interval: Every 2 Minutes                      ║
║      Dashboard: https://www.aiserviceco.com/dashboard   ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    while True:
        progress = load_progress()
        
        if progress['count'] >= DAILY_GOAL:
            print(f"\n🎉 DAILY GOAL ACHIEVED! {progress['count']}/{DAILY_GOAL}")
            print(f"   Batches completed: {progress['batches']}")
            print(f"   Dashboard: https://www.aiserviceco.com/dashboard.html")
            break
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 Launching Batch #{progress['batches'] + 1}")
        print(f"   Progress: {progress['count']}/{DAILY_GOAL}")
        
        # Run campaign
        batch_count = run_campaign_batch()
        
        # Update progress
        progress['count'] += batch_count
        progress['batches'] += 1
        save_progress(progress)
        
        print(f"   ✅ Batch complete: +{batch_count} outreach")
        print(f"   New total: {progress['count']}/{DAILY_GOAL}")
        
        if progress['count'] >= DAILY_GOAL:
            print(f"\n🎉 GOAL REACHED!")
            break
        
        # Wait for next interval
        print(f"   ⏳ Next batch in 2 minutes...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
