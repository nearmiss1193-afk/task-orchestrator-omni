"""
AGENT TRAINING SYSTEM - Fetch and learn from call center datasets
Sources: Hugging Face CallCenterEN, Mozilla Common Voice, Contact Center Audio
"""
import requests
import json
from datetime import datetime
import random

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# Dataset sources
DATASETS = {
    "callcenter_en": {
        "url": "https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english",
        "api": "https://datasets-server.huggingface.co/rows?dataset=AIxBlock%2F92k-real-world-call-center-scripts-english&config=default&split=train&offset=0&length=100",
        "description": "91,700 real call center transcripts",
        "license": "CC BY-NC 4.0"
    },
    "contact_center": {
        "url": "https://huggingface.co/datasets/AxonData/english-contact-center-audio-dataset",
        "description": "1,000+ hours of contact center audio + transcripts",
        "license": "Research"
    }
}

# Persuasion and objection patterns to extract
EXTRACTION_PATTERNS = {
    "objection_phrases": [
        "too expensive", "not interested", "already have", "call back later",
        "no time", "need to think", "talk to", "not ready", "budget",
        "competitor", "not right now", "maybe later"
    ],
    "closing_phrases": [
        "sounds good", "let's do it", "sign me up", "go ahead", "book it",
        "interested", "tell me more", "how do i", "when can", "yes"
    ],
    "persuasion_cues": [
        "imagine", "what if", "because", "results", "guarantee", "proven",
        "save", "quick", "easy", "simple", "free", "limited", "exclusive"
    ],
    "empathy_phrases": [
        "i understand", "that makes sense", "i hear you", "absolutely",
        "of course", "no problem", "happy to help", "great question"
    ]
}


def fetch_huggingface_sample(dataset_id: str, num_samples: int = 50) -> list:
    """Fetch sample rows from a Hugging Face dataset"""
    print(f"[FETCH] Fetching {num_samples} samples from {dataset_id}...")
    
    api_url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_id}&config=default&split=train&offset=0&length={num_samples}"
    
    try:
        r = requests.get(api_url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            rows = data.get("rows", [])
            print(f"  ✅ Fetched {len(rows)} rows")
            return rows
        else:
            print(f"  ❌ Failed: {r.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def extract_patterns(text: str) -> dict:
    """Extract persuasion and objection patterns from text"""
    text_lower = text.lower()
    
    patterns = {
        "objections_found": [],
        "closing_triggers": [],
        "persuasion_elements": [],
        "empathy_markers": [],
        "sentiment": "neutral"
    }
    
    # Find objections
    for phrase in EXTRACTION_PATTERNS["objection_phrases"]:
        if phrase in text_lower:
            patterns["objections_found"].append(phrase)
    
    # Find closing triggers
    for phrase in EXTRACTION_PATTERNS["closing_phrases"]:
        if phrase in text_lower:
            patterns["closing_triggers"].append(phrase)
    
    # Find persuasion cues
    for phrase in EXTRACTION_PATTERNS["persuasion_cues"]:
        if phrase in text_lower:
            patterns["persuasion_elements"].append(phrase)
    
    # Find empathy markers
    for phrase in EXTRACTION_PATTERNS["empathy_phrases"]:
        if phrase in text_lower:
            patterns["empathy_markers"].append(phrase)
    
    # Determine sentiment
    if patterns["closing_triggers"]:
        patterns["sentiment"] = "positive"
    elif patterns["objections_found"]:
        patterns["sentiment"] = "hesitant"
    
    return patterns


def process_transcript(transcript: dict) -> dict:
    """Process a single transcript into learning format"""
    # Extract text - handle different formats
    if isinstance(transcript, dict):
        text = transcript.get("row", {}).get("text", "") or transcript.get("text", "") or transcript.get("conversation", "")
        if isinstance(text, list):
            text = " ".join([str(t) for t in text])
    else:
        text = str(transcript)
    
    patterns = extract_patterns(text)
    
    return {
        "raw_text": text[:2000],  # Limit length
        "scenario": "call_center",
        "patterns": patterns,
        "has_objection": len(patterns["objections_found"]) > 0,
        "has_closing": len(patterns["closing_triggers"]) > 0,
        "persuasion_count": len(patterns["persuasion_elements"]),
        "empathy_count": len(patterns["empathy_markers"]),
        "sentiment": patterns["sentiment"]
    }


def store_training_example(example: dict) -> bool:
    """Store processed example in Supabase"""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/training_data",
            headers=HEADERS,
            json={
                "raw_text": example["raw_text"],
                "scenario": example["scenario"],
                "outcome": "positive" if example["has_closing"] else "neutral",
                "takeaways": json.dumps([
                    f"Objections: {example['patterns']['objections_found']}",
                    f"Closing triggers: {example['patterns']['closing_triggers']}",
                    f"Persuasion: {example['patterns']['persuasion_elements']}"
                ]),
                "emotional_cues": json.dumps(example["patterns"]),
                "agent": "training",
                "learning_extracted": True
            },
            timeout=15
        )
        return r.status_code in [200, 201]
    except:
        return False


def analyze_dataset(examples: list) -> dict:
    """Analyze patterns across all examples"""
    analysis = {
        "total_examples": len(examples),
        "with_objections": 0,
        "with_closing": 0,
        "objection_frequency": {},
        "closing_frequency": {},
        "persuasion_frequency": {},
        "avg_persuasion_count": 0,
        "avg_empathy_count": 0
    }
    
    total_persuasion = 0
    total_empathy = 0
    
    for ex in examples:
        if ex["has_objection"]:
            analysis["with_objections"] += 1
        if ex["has_closing"]:
            analysis["with_closing"] += 1
        
        total_persuasion += ex["persuasion_count"]
        total_empathy += ex["empathy_count"]
        
        # Track frequencies
        for obj in ex["patterns"]["objections_found"]:
            analysis["objection_frequency"][obj] = analysis["objection_frequency"].get(obj, 0) + 1
        for close in ex["patterns"]["closing_triggers"]:
            analysis["closing_frequency"][close] = analysis["closing_frequency"].get(close, 0) + 1
        for pers in ex["patterns"]["persuasion_elements"]:
            analysis["persuasion_frequency"][pers] = analysis["persuasion_frequency"].get(pers, 0) + 1
    
    if len(examples) > 0:
        analysis["avg_persuasion_count"] = total_persuasion / len(examples)
        analysis["avg_empathy_count"] = total_empathy / len(examples)
    
    return analysis


def generate_learning_insights(analysis: dict) -> list:
    """Generate actionable insights from analysis"""
    insights = []
    
    # Top objections
    top_objections = sorted(analysis["objection_frequency"].items(), key=lambda x: x[1], reverse=True)[:5]
    insights.append(f"Top objections: {', '.join([o[0] for o in top_objections])}")
    
    # Top closing triggers
    top_closing = sorted(analysis["closing_frequency"].items(), key=lambda x: x[1], reverse=True)[:5]
    insights.append(f"Top closing triggers: {', '.join([c[0] for c in top_closing])}")
    
    # Top persuasion elements
    top_persuasion = sorted(analysis["persuasion_frequency"].items(), key=lambda x: x[1], reverse=True)[:5]
    insights.append(f"Effective persuasion: {', '.join([p[0] for p in top_persuasion])}")
    
    # Conversion insights
    if analysis["total_examples"] > 0:
        close_rate = analysis["with_closing"] / analysis["total_examples"]
        insights.append(f"Closing rate in corpus: {close_rate:.1%}")
    
    return insights


def run_training_session():
    """Run a full training session"""
    print("=" * 60)
    print(f"AGENT TRAINING SESSION - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Fetch from CallCenterEN
    print("\n[1] Fetching CallCenterEN dataset...")
    rows = fetch_huggingface_sample("AIxBlock/92k-real-world-call-center-scripts-english", 50)
    
    if not rows:
        print("  ⚠️ Could not fetch dataset, using synthetic examples...")
        # Generate synthetic training data
        rows = generate_synthetic_examples()
    
    # Process transcripts
    print("\n[2] Processing transcripts...")
    processed = []
    for row in rows:
        example = process_transcript(row)
        if example["raw_text"]:
            processed.append(example)
    print(f"  ✅ Processed {len(processed)} examples")
    
    # Analyze patterns
    print("\n[3] Analyzing patterns...")
    analysis = analyze_dataset(processed)
    print(f"  • Examples with objections: {analysis['with_objections']}")
    print(f"  • Examples with closing: {analysis['with_closing']}")
    print(f"  • Avg persuasion elements: {analysis['avg_persuasion_count']:.1f}")
    
    # Generate insights
    print("\n[4] Generating learning insights...")
    insights = generate_learning_insights(analysis)
    for insight in insights:
        print(f"  📊 {insight}")
    
    # Store to Supabase
    print("\n[5] Storing training data...")
    stored = 0
    for ex in processed[:20]:  # Store first 20
        if store_training_example(ex):
            stored += 1
    print(f"  ✅ Stored {stored} examples to Supabase")
    
    # Summary
    print("\n" + "=" * 60)
    print("TRAINING SESSION COMPLETE")
    print("=" * 60)
    print(f"Total processed: {len(processed)}")
    print(f"Stored to DB: {stored}")
    print(f"Top objection: {list(analysis['objection_frequency'].keys())[:3] if analysis['objection_frequency'] else 'None'}")
    print(f"Top closing: {list(analysis['closing_frequency'].keys())[:3] if analysis['closing_frequency'] else 'None'}")
    
    return {
        "processed": len(processed),
        "stored": stored,
        "analysis": analysis,
        "insights": insights
    }


def generate_synthetic_examples() -> list:
    """Generate synthetic training examples based on patterns"""
    examples = [
        {"text": "Hi, I'm calling about your HVAC services. We've been having issues with missed calls. Agent: I understand, that's frustrating. Let me show you how we can help. What's your team size? Customer: About 5 techs. Agent: Perfect, our system works great for teams that size. Let's book a quick 15-minute demo."},
        {"text": "Customer: How much does this cost? Agent: Our pricing starts at $297 per month. Most teams see ROI within weeks from additional bookings. Customer: That sounds expensive. Agent: I understand budget is important. What if I showed you exactly how much revenue you're missing from those calls?"},
        {"text": "Agent: Hi, this is Christina from AI Service Co. Customer: I'm not interested right now. Agent: I hear you - timing matters. Quick question though - are you losing calls to competitors? Customer: Maybe, I don't know. Agent: That's exactly what our 15-minute audit reveals. No commitment."},
        {"text": "Customer: I need to talk to my partner first. Agent: Absolutely, let's include them. When would work for both of you? Customer: Maybe next week? Agent: Perfect, I'll send a calendar link for Tuesday or Wednesday."},
        {"text": "Agent: Based on your industry, you're likely missing 20-30% of potential customers. Customer: Really? Agent: Yes, and our system catches those automatically. Interested in seeing how? Customer: Sure, tell me more."},
    ]
    return [{"row": {"text": e["text"]}} for e in examples]


if __name__ == "__main__":
    run_training_session()
