"""
LARGE SCALE DATA INGESTION - Multi-dataset training pipeline
Fetches from Hugging Face datasets and loads into Supabase
"""
import requests
import json
from datetime import datetime
import time

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# All available datasets
DATASETS = {
    "callcenter_92k": {
        "id": "AIxBlock/92k-real-world-call-center-scripts-english",
        "name": "92k Call Center Transcripts",
        "description": "91,706 real call center conversations (~10,500 hours)",
        "type": "call_center",
        "license": "CC BY-NC 4.0"
    },
    "contact_center": {
        "id": "AxonData/english-contact-center-audio-dataset",
        "name": "Contact Center Audio + Transcripts",
        "description": "1,000+ hours of real call center audio with transcripts",
        "type": "contact_center",
        "license": "Research"
    },
    "saas_sales": {
        "id": "DeepMostInnovations/saas-sales-conversations",
        "name": "SaaS Sales Conversations",
        "description": "Sales conversations with conversion outcomes",
        "type": "sales",
        "license": "Open"
    }
}

# Pattern extraction
PATTERNS = {
    "objection": [
        "too expensive", "not interested", "already have", "call back later",
        "no time", "need to think", "talk to", "not ready", "budget", "competitor",
        "not right now", "maybe later", "don't need", "happy with", "can't afford"
    ],
    "closing": [
        "sounds good", "let's do it", "sign me up", "go ahead", "book it",
        "interested", "tell me more", "how do i", "when can", "yes", "perfect",
        "great", "schedule", "count me in"
    ],
    "persuasion": [
        "imagine", "what if", "because", "results", "guarantee", "proven",
        "save", "quick", "easy", "simple", "free", "limited", "exclusive",
        "opportunity", "benefit", "value"
    ],
    "empathy": [
        "i understand", "that makes sense", "i hear you", "absolutely",
        "of course", "no problem", "happy to help", "great question",
        "completely", "totally get it"
    ],
    "urgency": [
        "limited time", "only today", "running out", "last chance", "deadline",
        "before", "ends", "hurry", "quickly", "now", "immediately"
    ],
    "rapport": [
        "nice to meet", "how are you", "thank you", "appreciate", "wonderful",
        "pleasure", "glad", "excited", "looking forward"
    ]
}


def fetch_dataset_rows(dataset_id: str, offset: int = 0, limit: int = 100) -> list:
    """Fetch rows from Hugging Face dataset API"""
    api_url = f"https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": dataset_id,
        "config": "default",
        "split": "train",
        "offset": offset,
        "length": limit
    }
    
    try:
        r = requests.get(api_url, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get("rows", [])
        else:
            print(f"  ⚠️ API returned {r.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def extract_text_from_row(row: dict) -> str:
    """Extract text content from various row formats"""
    if isinstance(row, dict):
        row_data = row.get("row", row)
        
        # Try common text fields
        for field in ["text", "conversation", "transcript", "content", "dialogue", "message"]:
            if field in row_data:
                val = row_data[field]
                if isinstance(val, str):
                    return val
                elif isinstance(val, list):
                    return " ".join([str(v) for v in val])
        
        # Try concatenating all string values
        texts = [str(v) for v in row_data.values() if isinstance(v, str) and len(str(v)) > 20]
        if texts:
            return " ".join(texts)
    
    return str(row)[:2000]


def extract_all_patterns(text: str) -> dict:
    """Extract all pattern types from text"""
    text_lower = text.lower()
    
    result = {
        "objections": [],
        "closing_signals": [],
        "persuasion_elements": [],
        "empathy_markers": [],
        "urgency_cues": [],
        "rapport_builders": [],
        "sentiment": "neutral",
        "conversion_likelihood": 0.5
    }
    
    for pattern_type, phrases in PATTERNS.items():
        key = pattern_type + "s" if not pattern_type.endswith("y") else pattern_type[:-1] + "ies"
        if key not in result:
            key = pattern_type + "_markers" if pattern_type == "empathy" else pattern_type + "_cues"
        
        found = [p for p in phrases if p in text_lower]
        
        if pattern_type == "objection":
            result["objections"] = found
        elif pattern_type == "closing":
            result["closing_signals"] = found
        elif pattern_type == "persuasion":
            result["persuasion_elements"] = found
        elif pattern_type == "empathy":
            result["empathy_markers"] = found
        elif pattern_type == "urgency":
            result["urgency_cues"] = found
        elif pattern_type == "rapport":
            result["rapport_builders"] = found
    
    # Calculate sentiment
    positive_count = len(result["closing_signals"]) + len(result["rapport_builders"])
    negative_count = len(result["objections"])
    
    if positive_count > negative_count + 1:
        result["sentiment"] = "positive"
    elif negative_count > positive_count + 1:
        result["sentiment"] = "negative"
    else:
        result["sentiment"] = "neutral"
    
    # Estimate conversion likelihood
    score = 0.5
    score += len(result["closing_signals"]) * 0.1
    score += len(result["persuasion_elements"]) * 0.05
    score += len(result["empathy_markers"]) * 0.05
    score -= len(result["objections"]) * 0.1
    result["conversion_likelihood"] = max(0, min(1, score))
    
    return result


def process_and_store(dataset_key: str, rows: list) -> dict:
    """Process rows and store to Supabase"""
    stats = {"processed": 0, "stored": 0, "errors": 0}
    dataset = DATASETS.get(dataset_key, {})
    
    for row in rows:
        try:
            text = extract_text_from_row(row)
            if len(text) < 50:
                continue
            
            patterns = extract_all_patterns(text)
            
            # Determine outcome based on patterns
            if patterns["closing_signals"]:
                outcome = "converted"
            elif patterns["objections"]:
                outcome = "objected"
            else:
                outcome = "neutral"
            
            # Store to Supabase
            data = {
                "raw_text": text[:3000],
                "scenario": dataset.get("type", "unknown"),
                "outcome": outcome,
                "takeaways": json.dumps([
                    f"Objections: {patterns['objections'][:3]}",
                    f"Closing: {patterns['closing_signals'][:3]}",
                    f"Sentiment: {patterns['sentiment']}"
                ]),
                "emotional_cues": json.dumps(patterns),
                "agent": "training_pipeline",
                "learning_extracted": True
            }
            
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/training_data",
                headers=HEADERS,
                json=data,
                timeout=10
            )
            
            if r.status_code in [200, 201]:
                stats["stored"] += 1
            else:
                stats["errors"] += 1
            
            stats["processed"] += 1
            
        except Exception as e:
            stats["errors"] += 1
    
    return stats


def run_full_ingestion(samples_per_dataset: int = 100):
    """Run full ingestion from all datasets"""
    print("=" * 70)
    print(f"LARGE SCALE DATA INGESTION - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    total_stats = {"processed": 0, "stored": 0, "errors": 0, "datasets": 0}
    all_patterns = {"objections": {}, "closing": {}, "persuasion": {}}
    
    for key, dataset in DATASETS.items():
        print(f"\n[DATASET] {dataset['name']}")
        print(f"  ID: {dataset['id']}")
        print(f"  Type: {dataset['type']}")
        
        # Fetch rows
        rows = fetch_dataset_rows(dataset["id"], limit=samples_per_dataset)
        print(f"  Fetched: {len(rows)} rows")
        
        if rows:
            # Process and store
            stats = process_and_store(key, rows)
            print(f"  Processed: {stats['processed']}, Stored: {stats['stored']}, Errors: {stats['errors']}")
            
            total_stats["processed"] += stats["processed"]
            total_stats["stored"] += stats["stored"]
            total_stats["errors"] += stats["errors"]
            total_stats["datasets"] += 1
            
            # Extract aggregate patterns
            for row in rows:
                text = extract_text_from_row(row)
                patterns = extract_all_patterns(text)
                
                for obj in patterns["objections"]:
                    all_patterns["objections"][obj] = all_patterns["objections"].get(obj, 0) + 1
                for close in patterns["closing_signals"]:
                    all_patterns["closing"][close] = all_patterns["closing"].get(close, 0) + 1
                for pers in patterns["persuasion_elements"]:
                    all_patterns["persuasion"][pers] = all_patterns["persuasion"].get(pers, 0) + 1
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)
    print(f"Datasets processed: {total_stats['datasets']}")
    print(f"Total rows processed: {total_stats['processed']}")
    print(f"Total stored to DB: {total_stats['stored']}")
    print(f"Errors: {total_stats['errors']}")
    
    # Top patterns
    print("\n📊 TOP PATTERNS LEARNED:")
    top_obj = sorted(all_patterns["objections"].items(), key=lambda x: x[1], reverse=True)[:5]
    top_close = sorted(all_patterns["closing"].items(), key=lambda x: x[1], reverse=True)[:5]
    top_pers = sorted(all_patterns["persuasion"].items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"  Top Objections: {[o[0] for o in top_obj]}")
    print(f"  Top Closing: {[c[0] for c in top_close]}")
    print(f"  Top Persuasion: {[p[0] for p in top_pers]}")
    
    return {
        "stats": total_stats,
        "patterns": all_patterns
    }


def generate_learning_report() -> dict:
    """Generate a learning report from stored training data"""
    print("\n[REPORT] Generating learning report from Supabase...")
    
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/training_data",
            headers=HEADERS,
            params={"limit": 500, "order": "created_at.desc"},
            timeout=30
        )
        
        if r.status_code != 200:
            return {"error": "Failed to fetch training data"}
        
        rows = r.json()
        
        report = {
            "total_examples": len(rows),
            "by_outcome": {},
            "by_scenario": {},
            "objection_frequency": {},
            "closing_frequency": {},
            "avg_conversion_likelihood": 0
        }
        
        total_likelihood = 0
        
        for row in rows:
            # Count by outcome
            outcome = row.get("outcome", "unknown")
            report["by_outcome"][outcome] = report["by_outcome"].get(outcome, 0) + 1
            
            # Count by scenario
            scenario = row.get("scenario", "unknown")
            report["by_scenario"][scenario] = report["by_scenario"].get(scenario, 0) + 1
            
            # Parse emotional cues
            try:
                cues = json.loads(row.get("emotional_cues", "{}"))
                total_likelihood += cues.get("conversion_likelihood", 0.5)
                
                for obj in cues.get("objections", []):
                    report["objection_frequency"][obj] = report["objection_frequency"].get(obj, 0) + 1
                for close in cues.get("closing_signals", []):
                    report["closing_frequency"][close] = report["closing_frequency"].get(close, 0) + 1
            except:
                pass
        
        if rows:
            report["avg_conversion_likelihood"] = total_likelihood / len(rows)
        
        return report
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Run ingestion
    result = run_full_ingestion(samples_per_dataset=50)
    
    # Generate report
    report = generate_learning_report()
    print(f"\n📈 Learning Report:")
    print(f"  Total examples: {report.get('total_examples', 0)}")
    print(f"  By outcome: {report.get('by_outcome', {})}")
    print(f"  Avg conversion likelihood: {report.get('avg_conversion_likelihood', 0):.2%}")
