
"""
Imperium Sovereign Diagnostic Script (v40.1)
Purpose: Run Modal build for deploy.py, capture Exit Codes and classify root causes.
"""

import subprocess, datetime, os, sys

# --- CONFIG ---
PROJECT_DIR = os.getcwd()
# Directing to Brain Artifacts directory for consistency if possible, but user asked for root.
# We will use the local directory as requested, but ensure it exists.
DIGEST_DIR = os.path.join(PROJECT_DIR, "sovereign_digests")
os.makedirs(DIGEST_DIR, exist_ok=True)

# --- STEP 1: Timestamped log name ---
timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
logfile = os.path.join(DIGEST_DIR, f"DEPLOY_DIAGNOSTIC_{timestamp}.md")

# --- STEP 2: Deployment command ---
cmd = ["python", "-m", "modal", "deploy", "deploy.py", "--no-cache"]

print(f"\n🚀 Running Modal deployment diagnostic at {timestamp}\n")
print(f"Command: {' '.join(cmd)}\n")

# --- STEP 3: Run deployment ---
# Using shell=True for Windows compatibility with python -m if needed, but list args usually safer without.
# However, for 'python -m modal', standard list is fine.
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

exit_code = result.returncode
stderr_lower = result.stderr.lower()

# --- STEP 4: Root Cause Classification ---
if exit_code == 0:
    cause = "SUCCESS"
elif "playwright" in stderr_lower:
    cause = "PLAYWRIGHT DEPENDENCY CONFLICT"
elif "apt" in stderr_lower or "package" in stderr_lower:
    cause = "APT PACKAGE INSTALL ERROR"
elif "network" in stderr_lower or "timeout" in stderr_lower:
    cause = "NETWORK TIMEOUT"
elif "permission" in stderr_lower:
    cause = "PERMISSIONS ERROR"
else:
    cause = "UNKNOWN SYSTEM FAULT"

# --- STEP 5: Write Markdown Log ---
with open(logfile, "w", encoding="utf-8") as f:
    f.write(f"## Modal Deployment Diagnostic Report\n\n")
    f.write(f"**Timestamp:** {timestamp}\n\n")
    f.write(f"**Exit Code:** {exit_code}\n\n")
    f.write(f"**Probable Cause:** {cause}\n\n")
    f.write(f"### Standard Output:\n\n")
    f.write(f"```\n{result.stdout[:2000]}\n```")
    f.write("\n\n### Error Output:\n\n")
    f.write(f"```\n{result.stderr[:2000]}\n```")

print(f"\n📄 Diagnostic complete — Exit Code: {exit_code} | Cause: {cause}")
print(f"🗂️ Report saved to: {logfile}\n")

# --- Optional Exit Handler ---
if exit_code != 0:
    sys.exit(exit_code)
