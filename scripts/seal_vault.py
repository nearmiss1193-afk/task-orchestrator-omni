import os
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
    """[Z-NETWORK] Simulates sealing by writing to strike_parity.log"""
    env_vars = get_env_vars()
    print(f"📦 Found {len(env_vars)} keys to seal.")
    
    log_file = "strike_parity.log"
    try:
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"\n[ULTIMATE KILL SWITCH] Vault Sealed (Simulated). Keys found: {list(env_vars.keys())}")
        print("✅ SUCCESS: Sovereign Vault Sealed (Simulated - No Subprocess).")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    seal_vault()
