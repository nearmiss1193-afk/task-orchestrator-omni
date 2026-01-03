
class PricingManager:
    """
    MISSION: DYNAMIC PRICING INTELLIGENCE
    Decides the optimal offer for a lead based on their size, niche, and volume.
    """

    def __init__(self):
        self.tiers = {
            "tier_1": {"name": "The Starter", "price": 297, "model": "SaaS", "pitch": "Cheaper than your phone bill."},
            "tier_2": {"name": "The Growth", "price": 1500, "model": "Retainer", "pitch": "Simulates a full SDR team."},
            "tier_3": {"name": "The Partner", "price": "15% Rev Share", "model": "Performance", "pitch": "We don't get paid until you do."}
        }

    def generate_offer(self, niche: str, monthly_revenue: int, lead_volume: int):
        """
        Input: Client Stats.
        Output: The Perfect Offer (Tier + Script + Justification).
        """
        
        # 1. WHALE LOGIC (High Ticket)
        high_ticket_niches = ["roofing", "solar", "medspa", "legal", "hvac"]
        if niche.lower() in high_ticket_niches and monthly_revenue >= 50000:
            return self._format_offer("tier_3", f"Since you're in {niche} doing over $50k, we shouldn't charge you a fee. Let's partner. We only take a slice of the deals we close.")

        # 2. GROWTH LOGIC (Mid-Sized)
        if monthly_revenue >= 20000:
            return self._format_offer("tier_2", f"You need volume. For $1,500/mo, we deploy the full 'Social Siege' and 'Predator' engine. It replaces a $5k/mo agency.")

        # 3. STARTER LOGIC (Small Business / Default)
        return self._format_offer("tier_1", f"Let's keep overhead low. For $297/mo, you get the AI Receptionist and Text Agent. It stops you from missing calls immediately.")

    def _format_offer(self, tier_key, logic_script):
        offer = self.tiers[tier_key]
        return {
            "tier_name": offer["name"],
            "price_point": offer["price"],
            "model": offer["model"],
            "spartan_script": logic_script,
            "justification": offer["pitch"]
        }

    def calculate_human_cost_comparison(self, lead_volume):
        """
        Returns how much a human would cost for this volume vs AI.
        Assume Human = $20/hr, handles 10 leads/hr.
        """
        human_hours = lead_volume / 10
        human_cost = human_hours * 20
        ai_cost = lead_volume * 1 # Approx $1 per lead processing
        savings = human_cost - ai_cost
        return {
            "human_cost": human_cost,
            "ai_cost": ai_cost,
            "savings": savings,
            "message": f"A human would cost ${human_cost}/mo. Our AI costs ~${ai_cost}. You save ${savings}."
        }
