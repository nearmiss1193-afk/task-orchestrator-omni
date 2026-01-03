
import re
import json

try:
    with open("model_list.log", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Regex to find "AVAILABLE: models/(...)"
    matches = re.findall(r"AVAILABLE: models/([a-zA-Z0-9\-\.]+)", content)
    
    # Filter for gemini models
    gemini_models = [m for m in matches if "gemini" in m.lower()]
    
    print(json.dumps(gemini_models, indent=2))
except Exception as e:
    print(f"Error: {e}")
