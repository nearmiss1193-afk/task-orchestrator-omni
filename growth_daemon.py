import time
import subprocess
import sys
from datetime import datetime

# CONFIG
LOOP_INTERVAL = 60  # Run every 60 seconds (Turbo Mode)

def run_daemon():
    print(f"🚀 Growth Daemon Started. Interval: {LOOP_INTERVAL}s")
    
    while True:
        try:
            print(f"\n[DAEMON] Running Cortex Loop at {datetime.now().strftime('%H:%M:%S')}...")
            
            # Execute cortex_loop.py as a subprocess
            result = subprocess.run([sys.executable, "cortex_loop.py"], capture_output=True, text=True)
            
            # Print Output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr}")
                
            print(f"[DAEMON] Sleeping for {LOOP_INTERVAL}s...")
            time.sleep(LOOP_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Daemon Stopped by User.")
            break
        except Exception as e:
            print(f"❌ Daemon Error: {e}")
            time.sleep(LOOP_INTERVAL)

if __name__ == "__main__":
    run_daemon()
