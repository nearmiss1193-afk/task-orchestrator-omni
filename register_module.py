
import argparse
import os
import datetime

def register_module():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--status", required=True)
    args = parser.parse_args()

    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] MODULE_REGISTERED | Name: {args.name} | Version: {args.version} | Status: {args.status}"
    
    print(f"[REGISTERING MODULE]: {args.name} {args.version}")
    
    logfile = "supervisor_logs/module_registry.log"
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
        
    # Also write to main supervisor log for redundancy
    main_log = f"supervisor_logs/MISSION34_LOG_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(main_log, "a", encoding="utf-8") as f:
        f.write(f"✅ MODULE_REGISTERED: {args.name}\n")
        
    print(f"[SUCCESS] Registered in {logfile}")

if __name__ == "__main__":
    register_module()
