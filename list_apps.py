
import subprocess

with open("apps_utf8.txt", "w", encoding="utf-8") as f:
    subprocess.run(["python", "-m", "modal", "app", "list"], stdout=f, text=True)
