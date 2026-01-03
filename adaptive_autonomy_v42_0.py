
import subprocess
import datetime
import os
import sys

# Execution Orchestrator for Mission 43
def run_command(cmd):
    print(f"\n> {cmd}")
    try:
        # Use shell=True to handle complex args properly in windows
        subprocess.run(cmd, check=True, shell=True) 
    except subprocess.CalledProcessError as e:
        print(f"❌ Command Failed: {e}")
        sys.exit(1)

def main():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    
    print("🚀 STARTING ADAPTIVE AUTONOMY PROTOCOL (v42.0)")
    
    # 1. Permission Matrix
    run_command('python update_permission_matrix.py --approver "CEO_Daniel_Coffman" --no_secondary --enforce strict')
    
    # 2. Discovery
    run_command(f'python controlled_discovery_v41_1.py --sources discovery_sources.txt --mode read-only --interval 6h --summarize true --output sovereign_digests/DISCOVERY_REPORT_{timestamp}.md')
    
    # 3. Opportunity Analysis
    run_command(f'python opportunity_analyzer.py --input sovereign_digests/DISCOVERY_REPORT_{timestamp}.md --generate-proposals --roi-threshold 15 --accuracy-min 0.92 --output sovereign_digests/EXECUTION_PROPOSALS_{timestamp}.md')
    
    # 4. Self Upgrade
    run_command('python enable_self_upgrade.py --modules qa,discovery,analytics --verify-tests true --notify owner@aiserviceco.com')
    
    # 5. Digest
    run_command(f'python generate_autonomy_digest.py --output sovereign_digests/AUTONOMY_DIGEST_{timestamp}.md')

    print("\n🏁 MISSION 43 COMPLETE.")
    print("✅ AUTONOMY_ACTIVE_AND_CONTROLLED")

if __name__ == "__main__":
    main()
