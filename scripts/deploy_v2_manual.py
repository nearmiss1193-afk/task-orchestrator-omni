import os
import subprocess
import sys

def deploy():
    print("🛠️ SOVEREIGN DEPLOYMENT UTILITY (VERIFIED CREDENTIALS)")
    
    # 1. Set Correct Credentials
    os.environ['MODAL_TOKEN_ID'] = 'ak-qST8SXxuqE6otM34OgijU3'
    os.environ['MODAL_TOKEN_SECRET'] = 'as-iDYIV1ugqjCj1R2c6t0gt9'
    
    # 2. Target File
    target = 'execution/v2/v2_master_fusion.py'
    app_name = 'v2-empire-fusion'
    
    print(f"🚀 Deploying {target} as {app_name}...")
    
    # 3. Run Command
    try:
        cmd = [sys.executable, '-m', 'modal', 'deploy', target, '--name', app_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ DEPLOYMENT SUCCESSFUL")
            print(result.stdout)
        else:
            print("❌ DEPLOYMENT FAILED")
            print("--- STDOUT ---")
            print(result.stdout)
            print("--- STDERR ---")
            print(result.stderr)
            
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    deploy()
