
import argparse
import os
import datetime

def log_mission():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--logfile", required=True)
    args = parser.parse_args()

    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] MISSION{args.mission}_{args.status.upper()} | Tag: {args.tag} | Status: {args.status}"
    
    print(f"📝 LOGGING: {log_entry}")
    
    os.makedirs(os.path.dirname(args.logfile), exist_ok=True)
    with open(args.logfile, "a") as f:
        f.write(log_entry + "\n")
        
    print(f"✅ Logged to {args.logfile}")

if __name__ == "__main__":
    log_mission()
