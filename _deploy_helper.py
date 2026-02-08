"""Helper script to deploy Modal without Windows encoding issues"""
import subprocess
import os
import sys

# Set encoding globally
os.environ['PYTHONIOENCODING'] = 'utf-8:backslashreplace'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'

# Run the deploy
result = subprocess.run(
    [sys.executable, '-m', 'modal', 'deploy', 'deploy.py'],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    capture_output=True,
    env={**os.environ}
)

# Write output to file to avoid encoding issues
with open('modal_deploy_log.txt', 'wb') as f:
    f.write(b"=== STDOUT ===\n")
    f.write(result.stdout)
    f.write(b"\n=== STDERR ===\n")
    f.write(result.stderr)
    f.write(f"\n=== EXIT CODE: {result.returncode} ===\n".encode())

print(f"Deploy completed with exit code: {result.returncode}")
print("Full log written to modal_deploy_log.txt")
