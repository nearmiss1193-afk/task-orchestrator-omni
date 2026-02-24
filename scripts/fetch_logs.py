import subprocess
import re

def fetch():
    try:
        # fetch logs for the last 30m
        result = subprocess.run(
            ["python", "-m", "modal", "app", "logs", "ghl-omni-automation"],
            capture_output=True,
            text=True
        )
        
        # strip ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', result.stdout + result.stderr)
        
        # print the last 50 lines to see what happened inside the outreach cron
        lines = clean_text.split('\n')
        for line in lines[-50:]:
            print(line)
            
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    fetch()
