"""
BATCH TRAINING RUNNER - Fetch larger samples with pagination
"""
import requests
import json
import time
from datetime import datetime

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

PATTERNS = {
    "objection": ["too expensive", "not interested", "already have", "call back later", "no time", "need to think", "not ready", "budget", "competitor"],
    "closing": ["sounds good", "let's do it", "sign me up", "interested", "tell me more", "yes", "perfect", "schedule"],
    "persuasion": ["imagine", "because", "results", "guarantee", "save", "quick", "easy", "free", "limited"]
}


def fetch_batch(dataset_id: str, offset: int, limit: int = 100) -> list:
    """Fetch a batch of rows"""
    try:
        r = requests.get(
            f"https://datasets-server.huggingface.co/rows",
            params={"dataset": dataset_id, "config": "default", "split": "train", "offset": offset, "length": limit},
            timeout=30
        )
        if r.status_code == 200:
            return r.json().get("rows", [])
        return []
    except:
        return []


def extract_patterns(text: str) -> dict:
    text_lower = text.lower()
    return {
        "objections": [p for p in PATTERNS["objection"] if p in text_lower],
        "closing": [p for p in PATTERNS["closing"] if p in text_lower],
        "persuasion": [p for p in PATTERNS["persuasion"] if p in text_lower]
    }


def store_batch(rows: list, source: str) -> int:
    stored = 0
    for row in rows:
        try:
            text = str(row.get("row", {}).get("text", "") or row.get("row", {}).get("conversation", "") or row.get("row", {}))[:2000]
            if len(text) < 50:
                continue
            
            patterns = extract_patterns(text)
            
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/training_data",
                headers=HEADERS,
                json={
                    "raw_text": text,
                    "scenario": source,
                    "outcome": "converted" if patterns["closing"] else "neutral",
                    "emotional_cues": json.dumps(patterns),
                    "agent": "batch_training",
                    "learning_extracted": True
                },
                timeout=10
            )
            if r.status_code in [200, 201]:
                stored += 1
        except:
            pass
    return stored


def run_large_batch():
    """Run larger batch with pagination"""
    print("=" * 60)
    print(f"LARGE BATCH TRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    datasets = [
        ("AIxBlock/92k-real-world-call-center-scripts-english", "call_center"),
        ("DeepMostInnovations/saas-sales-conversations", "sales")
    ]
    
    total = {"fetched": 0, "stored": 0}
    all_patterns = {"objections": {}, "closing": {}, "persuasion": {}}
    
    for dataset_id, source in datasets:
        print(f"\n[DATASET] {source}")
        
        # Fetch multiple batches
        for batch_num in range(5):  # 5 batches of 100 = 500
            offset = batch_num * 100
            print(f"  Batch {batch_num + 1}/5 (offset {offset})...")
            
            rows = fetch_batch(dataset_id, offset, 100)
            if not rows:
                print(f"    No more rows")
                break
            
            print(f"    Fetched {len(rows)} rows")
            total["fetched"] += len(rows)
            
            # Extract patterns
            for row in rows:
                text = str(row.get("row", {}))
                patterns = extract_patterns(text)
                for obj in patterns["objections"]:
                    all_patterns["objections"][obj] = all_patterns["objections"].get(obj, 0) + 1
                for close in patterns["closing"]:
                    all_patterns["closing"][close] = all_patterns["closing"].get(close, 0) + 1
                for pers in patterns["persuasion"]:
                    all_patterns["persuasion"][pers] = all_patterns["persuasion"].get(pers, 0) + 1
            
            # Store
            stored = store_batch(rows, source)
            total["stored"] += stored
            print(f"    Stored {stored} to Supabase")
            
            time.sleep(2)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print("LARGE BATCH COMPLETE")
    print("=" * 60)
    print(f"Total fetched: {total['fetched']}")
    print(f"Total stored: {total['stored']}")
    
    top_obj = sorted(all_patterns["objections"].items(), key=lambda x: x[1], reverse=True)[:5]
    top_close = sorted(all_patterns["closing"].items(), key=lambda x: x[1], reverse=True)[:5]
    top_pers = sorted(all_patterns["persuasion"].items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"\n📊 TOP PATTERNS:")
    print(f"  Objections: {[o[0] for o in top_obj]}")
    print(f"  Closing: {[c[0] for c in top_close]}")
    print(f"  Persuasion: {[p[0] for p in top_pers]}")
    
    return total


if __name__ == "__main__":
    run_large_batch()
