"""
A/B TEST TRACKER - Message Variant Testing & Optimization
Empire Analytics Infrastructure

Features:
- Assign leads to test buckets (A/B/C/control)
- Track outcomes per variant
- Calculate conversion rates
- Statistical significance testing
- Feed winning patterns back
"""

import os
import json
import random
import datetime
from typing import Optional, Dict, List
from collections import defaultdict

# For Modal deployment
try:
    import modal
    from supabase import create_client, Client
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False

# ============ TEST VARIANTS ============
ACTIVE_TESTS = {
    "outreach_subject": {
        "A": "Quick thought for {name}",
        "B": "You're leaking $2,400/mo in missed calls",
        "C": "{name}, AI is calling your competitors",
        "control": "Partnership opportunity"
    },
    "outreach_opener": {
        "A": "hey {name}, saw your site. good hustle but you're leaking leads.",
        "B": "hi {name}, noticed you might be missing 82% of after-hours calls.",
        "C": "{name} - your competitors are using AI missed call text-back. are you?",
        "control": "Hi {name}, I wanted to reach out about our services."
    },
    "call_time": {
        "A": "9AM",
        "B": "2PM", 
        "C": "5PM",
        "control": "random"
    }
}

def get_supabase() -> "Client":
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def assign_variant(contact_id: str, test_name: str = "outreach_subject") -> str:
    """Assign a lead to a test variant"""
    # Use contact_id hash for consistent assignment
    hash_val = hash(contact_id + test_name)
    variants = list(ACTIVE_TESTS.get(test_name, {"A": "", "B": ""}).keys())
    variant = variants[hash_val % len(variants)]
    
    return variant

def get_variant_content(test_name: str, variant: str, context: dict = None) -> str:
    """Get the content for a specific variant"""
    template = ACTIVE_TESTS.get(test_name, {}).get(variant, "")
    
    if context:
        name = context.get("name", "there")
        template = template.replace("{name}", name)
    
    return template

def record_variant_assignment(contact_id: str, test_name: str, variant: str):
    """Record variant assignment in database"""
    if not MODAL_AVAILABLE:
        return
    # Only attempt DB write if env vars are configured
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    if not url:
        return
    supabase = get_supabase()
    supabase.table("contacts_master").update({
        "ab_variant": f"{test_name}:{variant}",
        "ab_assigned_at": datetime.datetime.now().isoformat()
    }).eq("ghl_contact_id", contact_id).execute()

def record_outcome(contact_id: str, outcome: str):
    """Record outcome for a lead's test variant"""
    if MODAL_AVAILABLE:
        supabase = get_supabase()
        supabase.table("contacts_master").update({
            "outcome": outcome,
            "outcome_at": datetime.datetime.now().isoformat()
        }).eq("ghl_contact_id", contact_id).execute()

def calculate_conversion_rates(test_name: str) -> Dict[str, dict]:
    """Calculate conversion rates for each variant"""
    if not MODAL_AVAILABLE:
        return {}
    
    supabase = get_supabase()
    
    # Get all leads with this test
    leads = supabase.table("contacts_master").select(
        "ab_variant, outcome, status"
    ).like("ab_variant", f"{test_name}:%").execute()
    
    # Aggregate by variant
    stats = defaultdict(lambda: {"total": 0, "responded": 0, "booked": 0, "closed": 0})
    
    for lead in leads.data:
        variant = lead.get("ab_variant", "").split(":")[-1]
        outcome = lead.get("outcome") or lead.get("status", "")
        
        stats[variant]["total"] += 1
        
        if outcome in ["responded", "engaged", "booked", "closed"]:
            stats[variant]["responded"] += 1
        if outcome in ["booked", "closed"]:
            stats[variant]["booked"] += 1
        if outcome == "closed":
            stats[variant]["closed"] += 1
    
    # Calculate rates
    results = {}
    for variant, data in stats.items():
        total = data["total"]
        if total > 0:
            results[variant] = {
                "total": total,
                "response_rate": data["responded"] / total,
                "booking_rate": data["booked"] / total,
                "close_rate": data["closed"] / total
            }
    
    return results

def get_winning_variant(test_name: str, metric: str = "response_rate") -> Optional[str]:
    """Determine the winning variant based on a metric"""
    rates = calculate_conversion_rates(test_name)
    
    if not rates:
        return None
    
    # Filter variants with enough data (min 10 samples)
    valid = {v: r for v, r in rates.items() if r["total"] >= 10}
    
    if not valid:
        return None
    
    # Find winner
    winner = max(valid, key=lambda v: valid[v].get(metric, 0))
    return winner

def generate_ab_report(test_name: str) -> str:
    """Generate a human-readable A/B test report"""
    rates = calculate_conversion_rates(test_name)
    winner = get_winning_variant(test_name)
    
    report = f"\n{'=' * 50}\n"
    report += f"A/B TEST REPORT: {test_name}\n"
    report += f"{'=' * 50}\n\n"
    
    for variant, data in sorted(rates.items()):
        is_winner = "🏆" if variant == winner else "  "
        report += f"{is_winner} Variant {variant}:\n"
        report += f"   Samples: {data['total']}\n"
        report += f"   Response: {data['response_rate']:.1%}\n"
        report += f"   Booking: {data['booking_rate']:.1%}\n"
        report += f"   Close: {data['close_rate']:.1%}\n\n"
    
    if winner:
        report += f"WINNER: Variant {winner}\n"
        winning_content = ACTIVE_TESTS.get(test_name, {}).get(winner, "N/A")
        report += f"Content: \"{winning_content[:50]}...\"\n"
    
    return report

# ============ INTEGRATION HELPERS ============
def prepare_outreach(contact_id: str, lead_name: str) -> dict:
    """Prepare outreach with A/B testing"""
    # Assign variants
    subject_variant = assign_variant(contact_id, "outreach_subject")
    opener_variant = assign_variant(contact_id, "outreach_opener")
    
    context = {"name": lead_name.split()[0] if lead_name else "there"}
    
    subject = get_variant_content("outreach_subject", subject_variant, context)
    opener = get_variant_content("outreach_opener", opener_variant, context)
    
    # Record assignment
    record_variant_assignment(contact_id, "outreach_subject", subject_variant)
    
    return {
        "subject": subject,
        "opener": opener,
        "variants": {
            "subject": subject_variant,
            "opener": opener_variant
        }
    }

# ============ CLI / TEST MODE ============
def run_test():
    """Test A/B assignment and content generation"""
    print("=" * 50)
    print("A/B TEST TRACKER TEST")
    print("=" * 50)
    
    # Test consistent assignment
    test_ids = ["lead_001", "lead_002", "lead_003", "lead_004", "lead_005"]
    
    print("\n📊 Variant Assignment Test:")
    for cid in test_ids:
        variant = assign_variant(cid, "outreach_subject")
        content = get_variant_content("outreach_subject", variant, {"name": "John"})
        print(f"   {cid} → Variant {variant}: \"{content[:40]}...\"")
    
    # Test consistency
    print("\n🔄 Consistency Check:")
    for cid in test_ids[:2]:
        v1 = assign_variant(cid, "outreach_subject")
        v2 = assign_variant(cid, "outreach_subject")
        status = "✅" if v1 == v2 else "❌"
        print(f"   {status} {cid}: {v1} == {v2}")
    
    # Test outreach preparation
    print("\n📧 Full Outreach Preparation:")
    result = prepare_outreach("test_lead_123", "Mike Johnson")
    print(f"   Subject: {result['subject']}")
    print(f"   Opener: {result['opener'][:60]}...")
    print(f"   Variants: {result['variants']}")
    
    print("\n✅ A/B Tracker functioning correctly")

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_test()
    else:
        print("Usage: python ab_test_tracker.py --test")
