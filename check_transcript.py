import sys, json
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

# Get recent calls - especially looking for today's with Dan's test
calls = sb.table("customer_memory").select("*").order("created_at", desc=True).limit(5).execute()

with open("transcript_output.txt", "w", encoding="utf-8") as f:
    for i, c in enumerate(calls.data):
        f.write("=" * 80 + "\n")
        f.write(f"CALL {i+1}\n")
        f.write(f"Phone: {c.get('phone_number', 'N/A')}\n")
        f.write(f"Created: {c.get('created_at', 'N/A')}\n")
        ctx = c.get("context_summary", {})
        if isinstance(ctx, str):
            f.write(f"TRANSCRIPT:\n{ctx}\n")
        elif isinstance(ctx, dict):
            f.write(json.dumps(ctx, indent=2, default=str) + "\n")
        f.write("\n")

print("Written to transcript_output.txt")
