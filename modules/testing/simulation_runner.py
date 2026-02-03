import os
import time
import subprocess
import requests

class SimulationRunner:
    """
    MISSION 39.4: CRISIS SIMULATION (Chaos Monkey)
    Orchestrates a controlled failure to test the Rollback Protocol.
    """
    def __init__(self):
        self.deployment_script = "deploy.py"
        self.broken_script = "deploy_broken.py"
        
    def prepare_broken_build(self):
        print("🔧 [SIMULATION] Generating Broken Build (QA Score = 0.7)...")
        with open(self.deployment_script, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Inject Hardcoded Failure
        # We replace the QA Score calculation with a fixed 0.7
        broken_content = content.replace(
            "qa_score = (chat_score * 0.4) + (cta_score * 0.3) + (contact_score * 0.3)",
            "qa_score = 0.7 # SIMULATED FAILURE"
        )
        
        with open(self.broken_script, "w", encoding="utf-8") as f:
            f.write(broken_content)
            
        print("⚠️ [SIMULATION] 'deploy_broken.py' created.")

    def trigger_failure(self):
        print("🚀 [SIMULATION] Deploying Broken Build...")
        # Deploy the broken script to Modal
        # This overwrites the named app "ghl-omni-automation"
        subprocess.run(["python", "-m", "modal", "deploy", self.broken_script, "--name", "ghl-omni-automation"], check=True)
        print("💥 [SIMULATION] Fault Injected. Governor should detect this shortly.")

    def monitor_recovery(self):
        print("️🕵️ [SIMULATION] Monitoring for Rollback...")
        # Polling DB / Logs for "ROLLBACK_EVENT"
        # In a real run, we'd wait for the cron or trigger it manually.
        # For this test, we might need to manually trigger the QA Routine on the broken deployment.
        print("   Triggering QA Routine on Broken Build...")
        subprocess.run(["python", "-m", "modal", "run", f"{self.broken_script}::governor_qa_routine"], check=False)
        
    def cleanup(self):
        print("🧹 [SIMULATION] Cleanup...")
        if os.path.exists(self.broken_script):
            os.remove(self.broken_script)

if __name__ == "__main__":
    sim = SimulationRunner()
    try:
        sim.prepare_broken_build()
        sim.trigger_failure()
        sim.monitor_recovery()
    finally:
        sim.cleanup()
