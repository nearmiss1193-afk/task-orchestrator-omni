import modal
# Try to find the app by name and print its web urls
try:
    # This might require an authenticated client
    app_name = "ghl-omni-automation"
    # Actually, we can't easily do this from the SDK without a running app.
    # We can try to use the CLI with more flags.
    import os
    os.system(f"python -m modal app list --json > apps_info.json")
except Exception as e:
    print(f"Error: {e}")
