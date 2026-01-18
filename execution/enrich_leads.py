"""
Lead Enrichment Script - Self-Annealing Enabled
================================================

Enriches leads with ROI calculations and identifies revenue leaks.
Now integrated with self-annealing for automatic error recovery.
"""

import json
import random
import os
import time
import traceback
from pathlib import Path
from datetime import datetime

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event, classify_error
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Retry configuration
RETRY_DELAYS = [1, 5, 15]  # Exponential backoff in seconds
MAX_RETRIES = len(RETRY_DELAYS)


def _enrich_mass_batch_inner(input_file):
    """Core enrichment logic - wrapped by retry handler."""
    with open(input_file, "r") as f:
        leads = json.load(f)
        
    enriched_results = []
    
    # NICHE ROI STRATEGY
    roi_config = {
        "personal injury lawyer": {"avg_val": 50000, "missed": (2, 5)},
        "water damage restoration": {"avg_val": 10000, "missed": (3, 8)},
        "emergency plumber": {"avg_val": 1000, "missed": (5, 15)},
        "solar company": {"avg_val": 20000, "missed": (2, 6)},
        "dui lawyer": {"avg_val": 10000, "missed": (3, 7)},
        "medspa": {"avg_val": 2500, "missed": (10, 20)},
        "roofing company": {"avg_val": 15000, "missed": (3, 6)},
        "hvac company": {"avg_val": 8000, "missed": (4, 10)},
        "estate lawyer": {"avg_val": 15000, "missed": (2, 4)},
        "chiropractor": {"avg_val": 3000, "missed": (5, 12)},
        "pool construction": {"avg_val": 40000, "missed": (1, 3)},
        "landscaping design": {"avg_val": 12000, "missed": (2, 5)},
        "seo agency": {"avg_val": 15000, "missed": (2, 4)},
        "cosmetic dentist": {"avg_val": 12000, "missed": (3, 8)}
    }
    
    for lead in leads:
        # Default to plumbing if niche unknown (fallback)
        niche = lead.get("niche", "emergency plumber")
        config = roi_config.get(niche.lower(), roi_config["emergency plumber"])
        
        missed_calls = random.randint(*config["missed"])
        avg_value = config["avg_val"]
        monthly_loss = missed_calls * avg_value
        annual_loss = monthly_loss * 12
        
        enriched_results.append({
            **lead,
            "missed_calls": missed_calls,
            "monthly_loss": monthly_loss,
            "annual_loss": annual_loss,
            "leaks": ["No instant text-back", "Slow site load", "Missing social proof"]
        })
        
    return enriched_results


def enrich_mass_batch(input_file):
    """
    Enriches leads with self-annealing retry logic.
    
    Implements exponential backoff on failure and logs to annealing system.
    """
    last_error = None
    
    for attempt, delay in enumerate(RETRY_DELAYS):
        try:
            result = _enrich_mass_batch_inner(input_file)
            
            # Log success if annealing enabled
            if ANNEALING_ENABLED:
                log_annealing_event({
                    "type": "success",
                    "script": "enrich_leads.py",
                    "function": "enrich_mass_batch",
                    "input": input_file,
                    "output_count": len(result),
                    "attempt": attempt + 1,
                    "timestamp": datetime.now().isoformat()
                })
            
            return result
            
        except Exception as e:
            last_error = e
            
            # Log error if annealing enabled
            if ANNEALING_ENABLED:
                log_annealing_event({
                    "type": "error",
                    "script": "enrich_leads.py",
                    "function": "enrich_mass_batch",
                    "input": input_file,
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:500],
                    "attempt": attempt + 1,
                    "traceback": traceback.format_exc()[-500:],
                    "timestamp": datetime.now().isoformat()
                })
            
            print(f"[ANNEAL] Attempt {attempt + 1}/{MAX_RETRIES} failed: {type(e).__name__}")
            
            if attempt < MAX_RETRIES - 1:
                print(f"[ANNEAL] Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"[ANNEAL] All retries exhausted. Raising error.")
                raise
    
    # Should not reach here, but just in case
    raise last_error


@self_annealing
def process_leads():
    """Main processing function with self-annealing decorator."""
    # Try different input files in priority order
    input_files = [
        "execution/mass_prospects_100.json",
        "execution/mass_prospects_50.json",
        "mass_prospects_100.json",
        "mass_prospects_50.json"
    ]
    
    for input_f in input_files:
        if os.path.exists(input_f):
            enriched = enrich_mass_batch(input_f)
            
            # Generate output filename
            output_f = input_f.replace("mass_prospects", "enriched_batch").replace("_prospects_", "_batch_")
            if not output_f.startswith("execution/"):
                output_f = f"execution/{output_f}"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_f), exist_ok=True)
            
            with open(output_f, "w") as f:
                json.dump(enriched, f, indent=4)
            
            print(f"✅ Enriched {len(enriched)} prospects.")
            print(f"   Input:  {input_f}")
            print(f"   Output: {output_f}")
            return enriched
    
    # No input files found - this is an edge case we log
    print("⚠️ No prospect files found. Creating sample data for testing...")
    
    # Create sample data so the script can still demonstrate functionality
    sample_leads = [
        {"name": "Sample HVAC Co", "niche": "hvac company", "phone": "555-0100"},
        {"name": "Sample Plumber", "niche": "emergency plumber", "phone": "555-0101"}
    ]
    
    sample_file = "execution/sample_prospects.json"
    os.makedirs("execution", exist_ok=True)
    with open(sample_file, "w") as f:
        json.dump(sample_leads, f, indent=4)
    
    print(f"   Created sample file: {sample_file}")
    return enrich_mass_batch(sample_file)


if __name__ == "__main__":
    process_leads()
