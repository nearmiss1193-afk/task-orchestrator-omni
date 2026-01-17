"""
HUGGING FACE AUTHENTICATED TRAINING - Use API token for full dataset access
"""
import requests
import json
import time
from datetime import datetime

# Hugging Face token
HF_TOKEN = "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"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
DB_HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

PATTERNS = {
    "objection": ["too expensive", "not interested", "already have", "call back later", "no time", "need to think", "not ready", "budget", "competitor", "don't need"],
    "closing": ["sounds good", "let's do it", "sign me up", "interested", "tell me more", "yes", "perfect", "schedule", "book", "ready"],
    "persuasion": ["imagine", "because", "results", "guarantee", "save", "quick", "easy", "free", "limited", "exclusive", "value"]
}


def fetch_with_auth(dataset_id: str, offset: int = 0, limit: int = 100) -> list:
    """Fetch from Hugging Face with authentication"""
    url = f"https://datasets-server.huggingface.co/rows"
    params = {"dataset": dataset_id, "config": "default", "split": "train", "offset": offset, "length": limit}
    
    try:
        r = requests.get(url, params=params, headers=HF_HEADERS, timeout=60)
        if r.status_code == 200:
            return r.json().get("rows", [])
        else:
            print(f"  ⚠️ Status {r.status_code}: {r.text[:100]}")
            return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def extract_patterns(text: str) -> dict:
    text_lower = text.lower()
    return {
        "objections": [p for p in PATTERNS["objection"] if p in text_lower],
        "closing": [p for p in PATTERNS["closing"] if p in text_lower],
        "persuasion": [p for p in PATTERNS["persuasion"] if p in text_lower]
    }


def store_example(text: str, source: str, patterns: dict) -> bool:
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/training_data",
            headers=DB_HEADERS,
            json={
                "raw_text": text[:2000],
                "scenario": source,
                "outcome": "converted" if patterns["closing"] else "neutral",
                "emotional_cues": json.dumps(patterns),
                "agent": "hf_training",
                "learning_extracted": True
            },
            timeout=10
        )
        return r.status_code in [200, 201]
    except:
        return False


def run_authenticated_training(samples_per_dataset: int = 500):
    """Run training with HF authentication for full access"""
    print("=" * 60)
    print(f"AUTHENTICATED HF TRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Token: hf_***{HF_TOKEN[-6:]}")
    print("=" * 60)
    
    datasets = [
        ("AIxBlock/92k-real-world-call-center-scripts-english", "call_center"),
        ("DeepMostInnovations/saas-sales-conversations", "sales")
    ]
    
    total = {"fetched": 0, "stored": 0}
    all_patterns = {"objections": {}, "closing": {}, "persuasion": {}}
    
    for dataset_id, source in datasets:
        print(f"\n[DATASET] {source} ({dataset_id})")
        
        batch_size = 100
        num_batches = samples_per_dataset // batch_size
        
        for batch in range(num_batches):
            offset = batch * batch_size
            print(f"  Batch {batch+1}/{num_batches} (offset {offset})...")
            
            rows = fetch_with_auth(dataset_id, offset, batch_size)
            if not rows:
                print(f"    No rows returned")
                break
            
            print(f"    Fetched {len(rows)} rows")
            total["fetched"] += len(rows)
            
            stored = 0
            for row in rows:
                row_data = row.get("row", row)
                text = str(row_data.get("text", "") or row_data.get("conversation", "") or row_data)[:2000]
                
                if len(text) < 50:
                    continue
                
                patterns = extract_patterns(text)
                
                # Track pattern frequencies
                for obj in patterns["objections"]:
                    all_patterns["objections"][obj] = all_patterns["objections"].get(obj, 0) + 1
                for close in patterns["closing"]:
                    all_patterns["closing"][close] = all_patterns["closing"].get(close, 0) + 1
                for pers in patterns["persuasion"]:
                    all_patterns["persuasion"][pers] = all_patterns["persuasion"].get(pers, 0) + 1
                
                if store_example(text, source, patterns):
                    stored += 1
            
            total["stored"] += stored
            print(f"    Stored {stored} examples")
            
            time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Total fetched: {total['fetched']}")
    print(f"Total stored: {total['stored']}")
    
    top_obj = sorted(all_patterns["objections"].items(), key=lambda x: x[1], reverse=True)[:5]
    top_close = sorted(all_patterns["closing"].items(), key=lambda x: x[1], reverse=True)[:5]
    top_pers = sorted(all_patterns["persuasion"].items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"\n📊 TOP PATTERNS LEARNED:")
    print(f"  Objections: {top_obj}")
    print(f"  Closing: {top_close}")
    print(f"  Persuasion: {top_pers}")
    
    return total


if __name__ == "__main__":
    run_authenticated_training(500)
