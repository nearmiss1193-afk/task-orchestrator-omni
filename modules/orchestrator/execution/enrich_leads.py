import json
import random
import os

def enrich_mass_batch(input_file):
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

if __name__ == "__main__":
    # Process the massive strike batch
    input_f = "execution/mass_prospects_100.json"
    if os.path.exists(input_f):
        enriched = enrich_mass_batch(input_f)
        output_f = "execution/enriched_batch_100.json"
        with open(output_f, "w") as f:
            json.dump(enriched, f, indent=4)
        print(f"✅ Enriched {len(enriched)} massive strike prospects.")
    else:
        # Fallback for 50 batch if needed
        input_f = "execution/mass_prospects_50.json"
        if os.path.exists(input_f):
            enriched = enrich_mass_batch(input_f)
            output_f = "execution/enriched_batch_50.json"
            with open(output_f, "w") as f:
                json.dump(enriched, f, indent=4)
            print(f"✅ Enriched {len(enriched)} mass prospects.")
        else:
            print(f"⚠️ No massive strike files found.")
