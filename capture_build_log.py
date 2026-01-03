
import subprocess
import os

# Define deploy command (Minimal arguments as advanced flags failed)
cmd = ["python", "-m", "modal", "deploy", "deploy.py"]

# Output path
output_file = r"c:\Users\nearm\.gemini\antigravity\brain\62b8ebe4-5452-4e67-bbf9-745834c0b6b3\sovereign_digests\BUILD_LOG_FINAL.txt"

print(f"Running: {' '.join(cmd)}")

try:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        cmd,
        cwd=r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Merge stdout/stderr
        text=True,
        encoding='utf-8', # Force encoding
        env=env
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Exit Code: {result.returncode}\n")
        f.write("-" * 20 + "\n")
        f.write(result.stdout)
        
    print(f"Log saved to: {output_file}")
    print(f"Exit Code: {result.returncode}")

except Exception as e:
    print(f"Error: {e}")
