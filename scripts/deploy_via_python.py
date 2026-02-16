import subprocess, sys, os
os.chdir(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified")
modal_path = os.path.join(os.environ["APPDATA"], "Python", "Python313", "Scripts", "modal.exe")
if not os.path.exists(modal_path):
    # Try finding it
    for root, dirs, files in os.walk(os.path.join(os.environ["APPDATA"], "Python")):
        if "modal.exe" in files:
            modal_path = os.path.join(root, "modal.exe")
            break
print(f"Using modal at: {modal_path}")
print(f"CWD: {os.getcwd()}")
result = subprocess.run([modal_path, "deploy", "workers/deploy.py"], capture_output=True, text=True)
print("STDOUT:", result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
print("Return code:", result.returncode)
