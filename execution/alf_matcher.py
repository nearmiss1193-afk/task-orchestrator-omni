"""
ALF Matcher - Facility Matching Engine
=======================================

Matches senior care clients to appropriate ALF facilities based on:
- Care level needs
- Budget range
- Location preference
- Specialties (memory care, etc.)
- Availability

Part of the ALF Referral Agency system.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

# Try Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@dataclass
class ClientNeeds:
    """Client requirements for facility matching."""
    care_level: str  # independent, light_assist, full_assist, memory_care
    budget_min: int
    budget_max: int
    preferred_city: Optional[str] = None
    preferred_county: Optional[str] = None
    max_distance_miles: int = 25
    specialties_needed: List[str] = None
    medicaid: bool = False  # CRITICAL - no commission if True


@dataclass
class FacilityMatch:
    """Matched facility with score."""
    facility_id: str
    name: str
    city: str
    monthly_rate_min: int
    monthly_rate_max: int
    match_score: float  # 0-100
    match_reasons: List[str]
    concerns: List[str]


class ALFMatcher:
    """
    Intelligent facility matching engine.
    """
    
    def __init__(self):
        """Initialize matcher with Supabase connection."""
        if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.db_connected = True
        else:
            self.supabase = None
            self.db_connected = False
            print("[ALF] Warning: Supabase not configured")
    
    @self_annealing
    def match_facilities(
        self,
        client: ClientNeeds,
        limit: int = 5
    ) -> List[FacilityMatch]:
        """
        Find best matching facilities for client needs.
        
        Args:
            client: ClientNeeds object with requirements
            limit: Max facilities to return
        
        Returns:
            List of FacilityMatch objects, sorted by score
        """
        # CRITICAL: Check Medicaid status
        if client.medicaid:
            print("[ALF] ⚠️ WARNING: Medicaid recipient - NO COMMISSION ALLOWED")
            # Still match, but flag prominently
        
        if not self.db_connected:
            print("[ALF] Database not connected - using mock data")
            return self._mock_matches(client)
        
        # Build query
        query = self.supabase.table("alf_facilities").select("*")
        
        # Filter by location
        if client.preferred_city:
            query = query.eq("city", client.preferred_city)
        elif client.preferred_county:
            query = query.eq("county", client.preferred_county)
        
        # Filter by budget (facility min rate <= client max budget)
        query = query.lte("monthly_rate_min", client.budget_max)
        
        # Filter by relationship status (only work with partners)
        query = query.in_("relationship_status", ["partner", "contracted", "prospect"])
        
        # Execute query
        result = query.execute()
        facilities = result.data if result.data else []
        
        # Score and rank
        scored = []
        for facility in facilities:
            score, reasons, concerns = self._score_facility(facility, client)
            if score > 0:
                scored.append(FacilityMatch(
                    facility_id=facility["id"],
                    name=facility["name"],
                    city=facility["city"],
                    monthly_rate_min=facility["monthly_rate_min"],
                    monthly_rate_max=facility["monthly_rate_max"],
                    match_score=score,
                    match_reasons=reasons,
                    concerns=concerns
                ))
        
        # Sort by score, return top matches
        scored.sort(key=lambda x: x.match_score, reverse=True)
        return scored[:limit]
    
    def _score_facility(
        self,
        facility: Dict,
        client: ClientNeeds
    ) -> tuple:
        """
        Score a facility against client needs.
        
        Returns:
            (score, reasons, concerns)
        """
        score = 50  # Base score
        reasons = []
        concerns = []
        
        # Budget fit (max 25 points)
        rate_min = facility.get("monthly_rate_min", 0)
        rate_max = facility.get("monthly_rate_max", 99999)
        
        if rate_min <= client.budget_max and rate_max >= client.budget_min:
            # Perfect budget overlap
            if rate_min >= client.budget_min and rate_max <= client.budget_max:
                score += 25
                reasons.append("Perfect budget fit")
            else:
                score += 15
                reasons.append("Within budget range")
        else:
            score -= 30
            concerns.append("Budget mismatch")
        
        # Care level match (max 20 points)
        care_levels = facility.get("care_levels", [])
        if client.care_level in care_levels:
            score += 20
            reasons.append(f"Offers {client.care_level} care")
        elif care_levels:
            score += 5
            concerns.append(f"May not offer {client.care_level}")
        
        # Specialties match (max 15 points)
        if client.specialties_needed:
            specialties = facility.get("specialties", [])
            matched = set(client.specialties_needed) & set(specialties)
            if matched:
                score += len(matched) * 5
                reasons.append(f"Specializes in: {', '.join(matched)}")
            else:
                concerns.append("Missing needed specialties")
        
        # Availability (max 10 points)
        availability = facility.get("current_availability", 0)
        if availability > 0:
            score += 10
            reasons.append(f"{availability} beds available")
        else:
            score -= 10
            concerns.append("No current availability listed")
        
        # Partner status (max 10 points)
        status = facility.get("relationship_status", "prospect")
        if status == "contracted":
            score += 10
            reasons.append("Contracted partner")
        elif status == "partner":
            score += 7
            reasons.append("Active partner")
        
        # AHCA rating bonus
        rating = facility.get("ahca_rating", "")
        if rating and "excellent" in rating.lower():
            score += 5
            reasons.append("Excellent AHCA rating")
        
        return max(0, min(100, score)), reasons, concerns
    
    def _mock_matches(self, client: ClientNeeds) -> List[FacilityMatch]:
        """Return mock data when DB not connected."""
        return [
            FacilityMatch(
                facility_id="mock-1",
                name="Sunrise Senior Living",
                city=client.preferred_city or "Orlando",
                monthly_rate_min=3500,
                monthly_rate_max=5500,
                match_score=85,
                match_reasons=["Good budget fit", "Memory care available"],
                concerns=[]
            ),
            FacilityMatch(
                facility_id="mock-2",
                name="Golden Years ALF",
                city=client.preferred_city or "Orlando",
                monthly_rate_min=3000,
                monthly_rate_max=4500,
                match_score=78,
                match_reasons=["Budget friendly", "High availability"],
                concerns=["Limited specialties"]
            )
        ]
    
    @self_annealing
    def create_referral(
        self,
        family_contact: str,
        family_phone: str,
        senior_name: str,
        care_level: str,
        budget_min: int,
        budget_max: int,
        preferred_city: str,
        source: str = "girlfriend_referral",
        medicaid: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new client referral in the database.
        
        Args:
            family_contact: Family member name
            family_phone: Contact phone
            senior_name: Senior's name
            care_level: Required care level
            budget_min: Minimum budget
            budget_max: Maximum budget
            preferred_city: Preferred location
            source: Lead source
            medicaid: Medicaid recipient status
            **kwargs: Additional fields
        
        Returns:
            Created referral record
        """
        if medicaid:
            print("[ALF] ⚠️ MEDICAID RECIPIENT - NO COMMISSION ELIGIBLE")
        
        referral = {
            "family_contact_name": family_contact,
            "family_phone": family_phone,
            "senior_name": senior_name,
            "care_level": care_level,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "preferred_city": preferred_city,
            "source": source,
            "medicaid_recipient": medicaid,
            "status": "intake",
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        
        if self.db_connected:
            result = self.supabase.table("alf_referrals").insert(referral).execute()
            referral = result.data[0] if result.data else referral
            print(f"[ALF] ✅ Referral created: {senior_name}")
        else:
            referral["id"] = f"local-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            print(f"[ALF] Referral created locally (DB not connected)")
        
        return {"success": True, "referral": referral}
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get current pipeline statistics.
        
        Returns:
            Pipeline metrics
        """
        if not self.db_connected:
            return {"error": "Database not connected"}
        
        stats = {
            "intake": 0,
            "matching": 0,
            "touring": 0,
            "placed": 0,
            "lost": 0,
            "total_active": 0,
            "pending_commission": 0,
            "collected_commission": 0
        }
        
        # Get referral counts by status
        result = self.supabase.table("alf_referrals").select("status, commission_amount, commission_status").execute()
        
        for ref in result.data or []:
            status = ref.get("status", "intake")
            if status in stats:
                stats[status] += 1
            
            if status not in ["lost"]:
                stats["total_active"] += 1
            
            commission = ref.get("commission_amount") or 0
            if ref.get("commission_status") == "paid":
                stats["collected_commission"] += commission
            elif ref.get("commission_status") in ["pending", "invoiced"]:
                stats["pending_commission"] += commission
        
        return stats
    
    def estimate_commission(
        self,
        monthly_rate: int,
        commission_rate: float = 1.0
    ) -> float:
        """
        Estimate commission for a placement.
        
        Args:
            monthly_rate: Facility monthly rate
            commission_rate: Commission percentage (1.0 = 100%)
        
        Returns:
            Estimated commission amount
        """
        return monthly_rate * commission_rate


# Convenience functions
def quick_match(
    budget_max: int,
    city: str,
    care_level: str = "assisted"
) -> List[FacilityMatch]:
    """Quick facility match."""
    matcher = ALFMatcher()
    needs = ClientNeeds(
        care_level=care_level,
        budget_min=0,
        budget_max=budget_max,
        preferred_city=city
    )
    return matcher.match_facilities(needs)


def new_referral(
    family_name: str,
    phone: str,
    senior: str,
    city: str,
    budget: int
) -> Dict:
    """Create new referral quickly."""
    matcher = ALFMatcher()
    return matcher.create_referral(
        family_contact=family_name,
        family_phone=phone,
        senior_name=senior,
        care_level="assisted",
        budget_min=0,
        budget_max=budget,
        preferred_city=city
    )


if __name__ == "__main__":
    print("[ALF] ALF Matcher - Facility Matching Engine")
    print("=" * 50)
    
    # Check configuration
    print()
    print("Configuration Status:")
    print(f"  Supabase: {'✅' if SUPABASE_URL else '⚠️ Not set'}")
    
    # Initialize matcher
    matcher = ALFMatcher()
    
    if matcher.db_connected:
        stats = matcher.get_pipeline_stats()
        print()
        print("Pipeline Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    print()
    print("[ALF] Commission Calculator:")
    print(f"  $4,000/month @ 100% = ${matcher.estimate_commission(4000):,.0f}")
    print(f"  $5,500/month @ 100% = ${matcher.estimate_commission(5500):,.0f}")
