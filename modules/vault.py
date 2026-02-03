import os

class SovereignVault:
    """
    The Internal Sovereign Vault.
    Authorized Access Only.
    """
    
    # GHL CONSTANTS (Executive Sovereign Account)
    GHL_LOCATION_ID = "RnK4OjX0oDcqtWw0VyLr"
    GHL_API_TOKEN = os.getenv("GHL_API_TOKEN", "managed_by_vault")
    
    # OUTREACH CREDENTIALS (REDUNDANCY)
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "managed_by_vault")
    GROK_API_KEY = os.getenv("GROK_API_KEY", "managed_by_vault")
    
    # SUPABASE (Mirroring Modal Secrets)
    SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "managed_by_vault")
    
    # VAPI (Standardized Voice)
    VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY", "managed_by_vault")
    VAPI_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
    VAPI_PHONE_ID = "8a7f18bf-8c1b-4aa661-8d5f-d622a12cb4f8"

    # BRIDGE CONFIG
    BRIDGE_URL = "https://empire-unified-backup-production-6d15.up.railway.app"
    SOVEREIGN_TOKEN = "sov-audit-2026-ghost"

    @classmethod
    def get_bridge_url(cls):
        return cls.BRIDGE_URL.rstrip('/')
    
VAULT = SovereignVault()
