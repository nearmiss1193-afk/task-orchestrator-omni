"""
Smoke & Vape Vertical Module - Phase 18
Board Mandate: Inventory-Aware Conversational AI
"""

from core.constants import SERVICE_KNOWLEDGE

VAPE_VERTICAL_KNOWLEDGE = SERVICE_KNOWLEDGE + """
SPECIALIZED VAPE/SMOKE SHOP LOGIC:
- Inventory Sync: Most shops struggle with real-time stock communication. Our AI can tell customers if a specific brand/flavor is in stock.
- Age Verification: AI reminds callers that valid ID is required for all purchases.
- Loyalty Programs: AI can check loyalty points (if connected to POS).
- Local SEO: Smoke shops rely heavily on Google Maps ranking. Our Review Gatekeeper is critical here.
"""

def get_vape_persona_injection(shop_name: str, stock_data: dict = None) -> str:
    """
    Returns vertical-specific prompt injection for Smoke/Vape shops.
    """
    stock_status = ""
    if stock_data:
        stock_status = "\nCURRENT STOCK ALERTS:\n"
        for item, status in stock_data.items():
            stock_status += f"- {item}: {status}\n"
            
    return f"""
    You are representing {shop_name}, a specialized Smoke & Vape destination.
    
    TONE: Knowledgeable, chill but professional, compliance-aware.
    
    KEY HOOKS:
    - "If we don't have your specific flavor, I can check if it's arriving on our next shipment."
    - "Just a reminder, we do require valid ID for everything in the shop."
    - "Have you joined our loyalty program yet? You get points on every bottle of juice."
    
    {stock_status}
    """

def analyze_vape_intent(transcript: str) -> dict:
    """
    Analyzes vape-specific intent (stock check, hours, price inquiry).
    """
    intents = {
        "stock_check": False,
        "price_inquiry": False,
        "loyalty_check": False
    }
    
    t = transcript.lower()
    if any(k in t for k in ["have", "stock", "in", "got", "carry", "brand", "flavor"]):
        intents["stock_check"] = True
    if any(k in t for k in ["price", "cost", "how much", "deal", "discount"]):
        intents["price_inquiry"] = True
    if any(k in t for k in ["point", "loyalty", "rewards", "member"]):
        intents["loyalty_check"] = True
        
    return intents
