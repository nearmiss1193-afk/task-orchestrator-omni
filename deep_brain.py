"""
DEEP BRAIN - Training Data Pipeline
====================================
Harvests call transcripts and successful interactions for LLM fine-tuning.
Creates the competitive moat through proprietary training data.
"""
import os
import json
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Configuration
OUTPUT_DIR = "deep_brain_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_supabase():
    """Get Supabase client."""
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def harvest_call_transcripts():
    """
    MISSION: Extract call transcripts for training data.
    Formats each call as a conversation for fine-tuning.
    """
    print("🧠 [DEEP BRAIN] Harvesting call transcripts...")
    
    supabase = get_supabase()
    
    try:
        # Fetch all call transcripts
        result = supabase.table("call_transcripts").select("*").execute()
        transcripts = result.data or []
        
        print(f"   Found {len(transcripts)} call records")
        
        training_data = []
        
        for call in transcripts:
            # Format as conversation for fine-tuning
            entry = format_call_for_training(call)
            if entry:
                training_data.append(entry)
        
        return training_data
        
    except Exception as e:
        print(f"   ❌ Error harvesting transcripts: {e}")
        return []

def harvest_successful_tasks():
    """
    MISSION: Extract successful task completions.
    These represent "what worked" for the AI to learn from.
    """
    print("🧠 [DEEP BRAIN] Harvesting successful tasks...")
    
    supabase = get_supabase()
    
    try:
        # Fetch completed tasks with positive outcomes
        result = supabase.table("tasks_queue").select("*").eq("status", "completed").execute()
        tasks = result.data or []
        
        print(f"   Found {len(tasks)} completed tasks")
        
        training_data = []
        
        for task in tasks:
            entry = format_task_for_training(task)
            if entry:
                training_data.append(entry)
        
        return training_data
        
    except Exception as e:
        print(f"   ❌ Error harvesting tasks: {e}")
        return []

def harvest_system_logs():
    """
    MISSION: Extract high-value system interactions.
    Filter for SUCCESS and LEAD entries only.
    """
    print("🧠 [DEEP BRAIN] Harvesting system logs...")
    
    supabase = get_supabase()
    
    try:
        # Fetch positive logs
        result = supabase.table("system_logs").select("*").in_("level", ["SUCCESS", "LEAD"]).limit(1000).execute()
        logs = result.data or []
        
        print(f"   Found {len(logs)} positive log entries")
        
        training_data = []
        
        for log in logs:
            entry = {
                "type": "system_success",
                "level": log.get("level"),
                "message": log.get("message"),
                "timestamp": log.get("created_at")
            }
            training_data.append(entry)
        
        return training_data
        
    except Exception as e:
        print(f"   ❌ Error harvesting logs: {e}")
        return []

def format_call_for_training(call: dict) -> dict:
    """Convert call record to JSONL training format."""
    
    transcript = call.get("transcript") or call.get("summary", "")
    if not transcript:
        return None
    
    # Format for instruction fine-tuning
    return {
        "instruction": "You are an AI phone receptionist. Handle this customer call professionally.",
        "input": f"Customer calling about: {call.get('intent', 'general inquiry')}",
        "output": transcript,
        "metadata": {
            "call_id": call.get("call_id"),
            "sentiment": call.get("sentiment"),
            "outcome": call.get("outcome", "unknown"),
            "source": "call_transcript"
        }
    }

def format_task_for_training(task: dict) -> dict:
    """Convert task record to training format."""
    
    return {
        "instruction": f"Execute task: {task.get('skill', 'unknown')}",
        "input": json.dumps(task.get("payload", {})),
        "output": f"Task completed successfully. Result: {task.get('result', 'completed')}",
        "metadata": {
            "task_id": task.get("id"),
            "skill": task.get("skill"),
            "campaign_id": task.get("campaign_id"),
            "source": "task_completion"
        }
    }

def export_to_jsonl(data: list, filename: str):
    """Export training data to JSONL format for fine-tuning."""
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"   ✅ Exported {len(data)} records to {filepath}")
    return filepath

def generate_training_dataset():
    """
    MASTER FUNCTION: Generate complete training dataset.
    Combines all sources into unified JSONL file.
    """
    print("=" * 60)
    print("🧠 DEEP BRAIN - Training Data Pipeline")
    print(f"   Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    all_data = []
    
    # Harvest from all sources
    call_data = harvest_call_transcripts()
    task_data = harvest_successful_tasks()
    log_data = harvest_system_logs()
    
    all_data.extend(call_data)
    all_data.extend(task_data)
    all_data.extend(log_data)
    
    print("-" * 60)
    print(f"📊 TOTAL RECORDS: {len(all_data)}")
    print(f"   - Calls: {len(call_data)}")
    print(f"   - Tasks: {len(task_data)}")
    print(f"   - Logs: {len(log_data)}")
    print("-" * 60)
    
    if all_data:
        # Export individual files
        if call_data:
            export_to_jsonl(call_data, "calls_training.jsonl")
        if task_data:
            export_to_jsonl(task_data, "tasks_training.jsonl")
        if log_data:
            export_to_jsonl(log_data, "logs_training.jsonl")
        
        # Export combined file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_file = export_to_jsonl(all_data, f"combined_training_{timestamp}.jsonl")
        
        print("=" * 60)
        print("✅ DEEP BRAIN HARVEST COMPLETE")
        print(f"   Output: {OUTPUT_DIR}/")
        print("=" * 60)
        
        return combined_file
    else:
        print("⚠️  No training data found. Make more calls!")
        return None

def analyze_training_quality():
    """Analyze the quality and distribution of training data."""
    
    print("\n📈 TRAINING DATA QUALITY ANALYSIS")
    print("-" * 40)
    
    # Check for JSONL files
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.jsonl')]
    
    if not files:
        print("No training files found. Run generate_training_dataset() first.")
        return
    
    for filename in files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        print(f"\n📄 {filename}")
        print(f"   Records: {len(lines)}")
        
        # Sample analysis
        if lines:
            sample = json.loads(lines[0])
            print(f"   Fields: {list(sample.keys())}")
            if 'metadata' in sample:
                print(f"   Metadata: {list(sample['metadata'].keys())}")

if __name__ == "__main__":
    # Run the full pipeline
    generate_training_dataset()
    analyze_training_quality()
