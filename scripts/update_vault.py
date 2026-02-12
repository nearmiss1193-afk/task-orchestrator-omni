"""Update sovereign-vault — override GOOGLE_API_KEY with the new Places-enabled key."""
import subprocess
from dotenv import dotenv_values

env = dotenv_values('.env')

# Override GOOGLE_API_KEY with the new Places-enabled key
env['GOOGLE_API_KEY'] = 'AIzaSyDVL4vfogtIKRLqOFNPMcKOg1LEAb9dipc'
env['GOOGLE_PLACES_API_KEY'] = 'AIzaSyDVL4vfogtIKRLqOFNPMcKOg1LEAb9dipc'

args = ['python', '-m', 'modal', 'secret', 'create', 'sovereign-vault', '--force']
for key, val in env.items():
    if val and not key.startswith('#'):
        args.append(f'{key}={val}')

print(f"Updating sovereign-vault — GOOGLE_API_KEY + GOOGLE_PLACES_API_KEY = AIzaSyDVL4v...")
r = subprocess.run(args, capture_output=True, text=True, timeout=30)
print(f"Exit code: {r.returncode}")
