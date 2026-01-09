"""
train_brain_industry.py - Load deep industry research into brain memory
"""
import psycopg2
import json
from datetime import datetime

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

# Industry intelligence data for brain
HVAC_DATA = {
    "industry": "HVAC",
    "avg_ticket": {"min": 5000, "max": 12500},
    "gross_margin": "40-55%",
    "net_margin": "10-25%",
    "pain_points": [
        "40% of calls go unanswered",
        "No 24/7 phone coverage",
        "Manual dispatch with spreadsheets",
        "Technician shortage (80k+ unfilled)",
        "Seasonal cash flow swings 40-60%",
        "Customer data scattered across paper/phones",
        "Office manager overwhelmed with phone duties"
    ],
    "key_metrics": {
        "emergency_call_value": "$350-500",
        "maintenance_agreement_annual": "$200-400",
        "missed_call_percentage": "40%",
        "dispatcher_jobs_per_day": "10-15",
        "office_manager_phone_time": "60%+"
    }
}

ROOFING_DATA = {
    "industry": "Roofing",
    "avg_ticket_residential": {"min": 7000, "max": 14500},
    "avg_ticket_commercial": {"min": 5000, "max": 200000},
    "gross_margin_residential": "30-40%",
    "gross_margin_commercial": "20-25%",
    "pain_points": [
        "Storm season overwhelms phones",
        "Quote follow-up falls through cracks",
        "Weather-dependent scheduling chaos",
        "Manual dispatch with paper/whiteboards",
        "CRM systems too rigid for roofing workflow",
        "Seasonal slowdowns (winter)",
        "Price shoppers waste time then ghost"
    ],
    "key_metrics": {
        "lead_value": "$7,000-14,500",
        "storm_calls_per_day": "50-200 during events",
        "quote_follow_up_failure": "30-50%"
    }
}

SALES_HOOKS = {
    "hvac": [
        "The After-Hours Problem: How many emergency calls do you miss after 5pm?",
        "The $500 Missed Call: Average service call is $350-500, missing 5-10/week = $2,000-5,000 to competitors",
        "Maintenance Agreement Growth: Auto-offer service agreements to every caller"
    ],
    "roofing": [
        "Storm Season Speed: Can your team handle 200 calls in 3 days?",
        "The Quote Follow-Up: AI follows up until they say yes or no",
        "The Referral Engine: Auto-ask for referrals after every job"
    ]
}

OBJECTION_RESPONSES = {
    "too_complicated": "Sarah's not software to learn. She's an employee who answers your phone.",
    "want_human": "Sarah IS having a conversation. 90% can't tell she's AI.",
    "makes_mistakes": "She's trained on your exact requirements. Unlike humans, never has a bad day.",
    "too_small": "You're the perfect size. Big companies have staff. You need AI to compete.",
    "sounds_expensive": "How much is one missed $500 emergency call? Sarah costs less than that per month.",
    "need_to_think": "Free trial. If Sarah doesn't book 5 new jobs in 14 days, no charge."
}

def train_brain():
    print("=" * 60)
    print("🧠 TRAINING BRAIN WITH INDUSTRY INTELLIGENCE")
    print("=" * 60)
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Store HVAC intelligence
    cur.execute("""
        INSERT INTO system_memory (key, value) 
        VALUES ('industry_hvac', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (json.dumps(HVAC_DATA),))
    print("✓ HVAC industry data loaded")
    
    # Store Roofing intelligence
    cur.execute("""
        INSERT INTO system_memory (key, value) 
        VALUES ('industry_roofing', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (json.dumps(ROOFING_DATA),))
    print("✓ Roofing industry data loaded")
    
    # Store Sales hooks
    cur.execute("""
        INSERT INTO system_memory (key, value) 
        VALUES ('sales_hooks', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (json.dumps(SALES_HOOKS),))
    print("✓ Sales hooks loaded")
    
    # Store Objection responses
    cur.execute("""
        INSERT INTO system_memory (key, value) 
        VALUES ('objection_responses', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (json.dumps(OBJECTION_RESPONSES),))
    print("✓ Objection responses loaded")
    
    # Store training summary
    training_summary = {
        "trained_at": datetime.now().isoformat(),
        "topics": ["HVAC", "Roofing", "Sales Hooks", "Objection Handling"],
        "data_points": len(HVAC_DATA["pain_points"]) + len(ROOFING_DATA["pain_points"]),
        "hooks_count": len(SALES_HOOKS["hvac"]) + len(SALES_HOOKS["roofing"]),
        "objections_count": len(OBJECTION_RESPONSES)
    }
    
    cur.execute("""
        INSERT INTO system_memory (key, value) 
        VALUES ('training_log', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (json.dumps(training_summary),))
    print("✓ Training log saved")
    
    conn.commit()
    
    # Verify
    print("\n📊 BRAIN MEMORY STATUS:")
    cur.execute("SELECT key FROM system_memory ORDER BY key")
    for r in cur.fetchall():
        print(f"  - {r[0]}")
    
    conn.close()
    print("\n✅ BRAIN TRAINING COMPLETE!")
    print(f"   Topics: {', '.join(training_summary['topics'])}")
    print(f"   Data Points: {training_summary['data_points']}")

if __name__ == "__main__":
    train_brain()
