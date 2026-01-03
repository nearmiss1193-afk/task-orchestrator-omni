
import subprocess
import json

def list_apps():
    try:
        # Run the command directly, capturing output as bytes
        result = subprocess.run(
            ["python", "-m", "modal", "app", "list", "--json"], 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"Error running modal app list: {result.stderr}")
            return

        # The output might be polluted with deprecation warnings or banners.
        # We need to find the specific JSON part. 
        # Modal CLI json output usually is the whole body, but let's be safe.
        output = result.stdout.strip()
        
        # Save to a known clean file
        with open("clean_apps.json", "w", encoding="utf-8") as f:
            f.write(output)
            
        print("Successfully wrote clean_apps.json")
        print("Preview start:", output[:200])

    except Exception as e:
        print(f"Failed to run diagnosis: {e}")

if __name__ == "__main__":
    list_apps()
