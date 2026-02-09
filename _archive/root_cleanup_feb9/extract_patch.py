
import json
import re

try:
    with open("voice_optimization_advice.md", "r") as f:
        content = f.read()
    
    # Find the JSON block
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        json_data = json.loads(match.group())
        print(json.dumps(json_data, indent=2))
        
        # Save it to apply
        with open("sarah_patch.json", "w") as f2:
            json.dump(json_data, f2, indent=2)
    else:
        print("No JSON found in advice.")
except Exception as e:
    print(f"Error: {e}")
