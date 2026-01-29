import os
import modal
import subprocess
from dotenv import load_dotenv

def get_env_vars():
    """Load and return all relevant environment variables."""
    # Load .env and .env.local
    load_dotenv(".env")
    load_dotenv(".env.local")
    
    env_dict = {
        # GHL
        "GHL_LOCATION_ID": os.getenv("GHL_LOCATION_ID"),
        "GHL_API_TOKEN": os.getenv("GHL_API_TOKEN"),
        "GHL_SMS_WEBHOOK_URL": os.getenv("GHL_SMS_WEBHOOK_URL"),
        
        # Supabase
        "SUPABASE_URL": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        
        # Stripe
        "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY"),
        "STRIPE_WEBHOOK_SECRET": os.getenv("STRIPE_WEBHOOK_SECRET"),
        
        # Vapi
        "VAPI_API_KEY": os.getenv("VAPI_API_KEY"),
        "VAPI_PHONE_NUMBER_ID": os.getenv("VAPI_PHONE_NUMBER_ID"),
        
        # AI
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GROK_API_KEY": os.getenv("GROK_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        
        # Others
        "HUNTER_API_KEY": os.getenv("HUNTER_API_KEY"),
        "LUSHA_API_KEY": os.getenv("LUSHA_API_KEY"),
        "RESEND_API_KEY": os.getenv("RESEND_API_KEY"),
    }
    
    # Filter out None values
    return {k: v for k, v in env_dict.items() if v is not None}

def seal_vault():
    """Create the Modal secret using CLI for maximum reliability."""
    env_vars = get_env_vars()
    print(f"📦 Found {len(env_vars)} keys to seal.")
    
    # Construct the command
    # modal secret create name KEY=VALUE KEY2=VALUE2
    cmd = ["modal", "secret", "create", "sovereign-vault"]
    for k, v in env_vars.items():
        cmd.append(f"{k}={v}")
    
    try:
        # Run CLI command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SUCCESS: Sovereign Vault Sealed.")
        else:
            print(f"❌ FAILED to seal vault: {result.stderr}")
    except Exception as e:
        print(f"❌ ERROR executing modal command: {e}")

if __name__ == "__main__":
    seal_vault()
