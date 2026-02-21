import sys
import os
import traceback

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.autonomous_inspector import Inspector

def test_autonomous_healing():
    inspector = Inspector()
    try:
        from workers.broken_worker import intentionally_broken_function
        intentionally_broken_function()
    except Exception as e:
        print("Crash caught. Routing to Abacus Self-Healing Pipeline...")
        # Note: The traceback MUST contain the file path `workers/broken_worker.py` for Abacus to know what to fix.
        # Calling handle_crash parses traceback and POSTs to webhook.
        inspector.handle_crash("test_autonomous_healing", e)

if __name__ == "__main__":
    test_autonomous_healing()
