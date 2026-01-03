
import modal
import os
import google.generativeai as genai

app = modal.App("debug-models")
image = modal.Image.debian_slim().pip_install("google-generativeai")
VAULT = modal.Secret.from_name("agency-vault")

@app.function(image=image, secrets=[VAULT])
def list_available_models():
    print("--- START MODEL LIST ---")
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        print(f"API Key Present: {bool(api_key)}")
        genai.configure(api_key=api_key)
        
        models = list(genai.list_models())
        print(f"Found {len(models)} models.")
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                print(f"AVAILABLE: {m.name}")
                
    except Exception as e:
        print(f"FAILURE: {e}")
    print("--- END MODEL LIST ---")

@app.local_entrypoint()
def main():
    list_available_models.remote()
