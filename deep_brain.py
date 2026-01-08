import os
import json
import time
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Keys missing.")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def harvest_and_format():
    print("🧠 Starting Deep Brain Harvest...")
    
    # 1. Fetch Transcripts
    try:
        res = supabase.table('call_transcripts').select("*").execute()
        transcripts = res.data
        print(f"   found {len(transcripts)} transcripts.")
    except Exception as e:
        print(f"   ❌ Error fetching transcripts: {e}")
        transcripts = []

    # 2. Format as JSONL
    # Format: {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
    
    dataset = []
    
    for t in transcripts:
        if not t.get('transcript'): continue
        
        # Simple heuristic: Split transcript by lines or speaker labels if available
        # For now, we assume transcript is a blob and valid "content"
        # Ideally, we parse "User: ... Agent: ..."
        
        entry = {
            "messages": [
                {"role": "system", "content": "You are Sarah, a top-tier HVAC sales assistant. You are witty, concise, and helpful."},
                {"role": "user", "content": "Incoming Call Interaction"}, 
                {"role": "assistant", "content": t['transcript']} # This is raw, likely needs parsing in V2
            ]
        }
        dataset.append(entry)
        
    # 3. Save to Disk
    filename = f"empire_training_data_{int(time.time())}.jsonl"
    with open(filename, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
            
    print(f"✅ Harvest Complete. Saved {len(dataset)} examples to {filename}")
    return filename

if __name__ == "__main__":
    harvest_and_format()
