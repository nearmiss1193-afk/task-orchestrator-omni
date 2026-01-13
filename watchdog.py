import subprocess
import time
import psutil
import os

# Configuration
TARGET_SCRIPT = os.path.abspath('continuous_swarm.py')
MAX_RUNTIME_SECONDS = 30 * 60  # 30 minutes
CHECK_INTERVAL = 60  # check every minute

def get_python_processes():
    """Return a list of (pid, create_time) for python processes running the target script."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['name'] and proc.info['name'].lower().startswith('python'):
                cmd = proc.info['cmdline']
                if cmd and TARGET_SCRIPT in cmd:
                    procs.append((proc.info['pid'], proc.info['create_time']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(5)
        except psutil.TimeoutExpired:
            p.kill()
        print(f"[watchdog] Killed process {pid}")
    except Exception as e:
        print(f"[watchdog] Error killing process {pid}: {e}")

def start_target():
    try:
        subprocess.Popen(['python', TARGET_SCRIPT], cwd=os.path.dirname(TARGET_SCRIPT))
        print(f"[watchdog] Restarted {TARGET_SCRIPT}")
    except Exception as e:
        print(f"[watchdog] Failed to start {TARGET_SCRIPT}: {e}")

if __name__ == '__main__':
    print('[watchdog] Starting watchdog...')
    while True:
        now = time.time()
        for pid, create_time in get_python_processes():
            runtime = now - create_time
            if runtime > MAX_RUNTIME_SECONDS:
                print(f"[watchdog] Process {pid} exceeded max runtime ({runtime}s). Restarting.")
                kill_process(pid)
                start_target()
        time.sleep(CHECK_INTERVAL)
