
import sys
import os
from deploy import deploy_ghl_site

if __name__ == "__main__":
    # Wrapper to run the deploy function locally or via Modal with specific arguments
    # This helps catch errors immediately in the console output
    try:
        # Simulate CLI args for the underlying function if needed, 
        # but deploy_ghl_site in deploy.py uses Modal's entrypoint machinery usually.
        # However, looking at deploy.py, deploy_ghl_site is:
        # @app.local_entrypoint()
        # def deploy_ghl_site(niche: str = "generic"):
        
        # We can call it directly if we import it, BUT it decorates with @app.local_entrypoint.
        # The best way to run it is weird via python script if we want to bypass 'modal run'.
        # Actually, let's just use 'modal run' in the run_command, 
        # but I created this wrapper to ensure clean execution context if I needed to use 'python wrapper.py'.
        # Since I'm using 'modal run' in the Tool Call, this file is just a backup test.
        pass
    except Exception as e:
        print(f"Wrapper Crash: {e}")
