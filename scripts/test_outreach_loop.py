import sys
import os

# Append root to path like the workers do
if "/root" not in sys.path:
    sys.path.append(os.getcwd())

from workers.outreach import auto_outreach_loop

print("--- TRIGGERING AUTO OUTREACH LOOP LOCALLY ---")
try:
    auto_outreach_loop()
except Exception as e:
    print(f"FAILED: {e}")
print("--- FINISHED ---")
