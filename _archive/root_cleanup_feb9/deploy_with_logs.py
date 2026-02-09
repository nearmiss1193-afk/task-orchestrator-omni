"""
Deploy script with full error capture
"""
import subprocess
import sys

print("🚀 Deploying to Modal...")
print("="*60)

result = subprocess.run(
    ["python", "-m", "modal", "deploy", "deploy.py"],
    capture_output=True,
    text=True,
    cwd=r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified"
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nExit code: {result.returncode}")

sys.exit(result.returncode)
