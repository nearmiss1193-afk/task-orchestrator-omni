
import subprocess

with open("apps.json", "w", encoding="utf-8") as f:
    subprocess.run(["python", "-m", "modal", "app", "list", "--json"], stdout=f, text=True)
