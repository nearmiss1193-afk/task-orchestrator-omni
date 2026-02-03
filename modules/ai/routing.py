import os
import json
import datetime
from modules.database.supabase_client import get_supabase

class HeuristicFallbackModel:
    """
    TIER 2 FALLBACK (Mock LLM)
    Activated when Gemini API fails repeatedly. Returns rule-based safe responses.
    """
    def generate_content(self, prompt):
        print("[Heuristic Engine] Intercepting request (Tier 2 Active)")
        class MockResponse:
            text = "system notice: ai model unavailable."
            
        p = prompt.lower()
        # Spartan Fallback (JSON)
        if "role: spartan" in p:
             MockResponse.text = '{"reply": "hey, saw your message. tied up right now but wanted to acknowledge. are you free later?", "confidence": 1.0, "intent": "info"}'
        # Governor Fallback (Text)
        elif "overseer" in p:
             MockResponse.text = "Governor Status: Tier 2 Fallback Active. Detailed analysis paused."
             
        return MockResponse()

def get_overseer():
    try:
        from modules.governor.internal_supervisor import InternalSupervisor
        return InternalSupervisor()
    except ImportError:
        return None

def get_gemini_model(model_type="flash"):
    """
    MISSION 39: DYNAMIC ROUTING
    Consults Engine Registry for best available model.
    """
    try:
        supabase = get_supabase()
        
        # 1. Ask Router (Mission 39)
        ov = get_overseer()
        best_engine = "gemini-flash"
        if ov:
            # We don't have get_best_engine implemented in InternalSupervisor yet based on my view_file
            # but deploy.py had it. I'll stick to what deploy.py was doing.
            try:
                best_engine = ov.get_best_engine(supabase)
            except AttributeError:
                pass
            
        # 2. Routing Logic
        if best_engine == "heuristic-mock":
            return HeuristicFallbackModel()
            
        elif best_engine == "anti-gravity":
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY") 
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-1.5-pro")
            
        # Default: Gemini Flash
        import google.generativeai as genai 
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        model_name = "gemini-1.5-flash"
        if model_type == "pro": model_name = "gemini-1.5-pro"
            
        return genai.GenerativeModel(model_name)

    except Exception as e:
        print(f"Routing Error: {e}. Defaulting to Flash.")
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
