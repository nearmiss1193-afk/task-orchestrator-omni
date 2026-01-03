
import os
import sys

# Setup Path
sys.path.append(os.getcwd())

from modules.governor.sovereign_ops_agent import SovereignOpsAgent

def main():
    print("🚀 Triggering Manual Sovereign Pulse...")
    agent = SovereignOpsAgent() # Default: Mock Mode if no keys
    
    # Run
    markdown = agent.run_daily_pulse()
    
    # Save to file for User Verification
    with open("sovereign_digests/FIRST_PULSE_OUTPUT.md", "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print("✅ First Pulse Generated at sovereign_digests/FIRST_PULSE_OUTPUT.md")

if __name__ == "__main__":
    main()
