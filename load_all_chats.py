import psycopg2
import os
import glob
import json
from datetime import datetime

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'
BRAIN_DIR = r'C:\Users\nearm\.gemini\antigravity\brain'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("=" * 60)
print("LOADING ALL CONVERSATIONS INTO BRAIN")
print("=" * 60)

# Get all conversation directories
conv_dirs = [d for d in glob.glob(os.path.join(BRAIN_DIR, '*')) if os.path.isdir(d)]
print(f"\nFound {len(conv_dirs)} conversation directories")

# Aggregate conversation data
conversations = []
for conv_dir in conv_dirs:
    conv_id = os.path.basename(conv_dir)
    if len(conv_id) < 30:  # Skip non-UUID
        continue
    
    # Check for key files
    files_found = []
    for filename in ['task.md', 'implementation_plan.md', 'walkthrough.md']:
        filepath = os.path.join(conv_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:2000]
                files_found.append({'name': filename, 'size': len(content)})
            except:
                pass
    
    if files_found:
        conversations.append({
            'id': conv_id[:8],
            'files': len(files_found),
            'types': [f['name'] for f in files_found]
        })

print(f"Loaded {len(conversations)} conversations with artifacts")

# Save to brain
conv_data = json.dumps({
    'count': len(conversations),
    'conversations': conversations[:50],  # Limit to 50 for storage
    'loaded_at': datetime.now().isoformat()
})

cur.execute("""
    INSERT INTO system_memory (key, value) 
    VALUES ('all_conversations', %s)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
""", (conv_data,))

conn.commit()

# Also check campaign status
print("\n" + "=" * 60)
print("CAMPAIGN STATUS")
print("=" * 60)

print("\n📊 LEADS:")
cur.execute("SELECT status, COUNT(*) FROM leads GROUP BY status ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[0] or 'null'}: {r[1]}")

print("\n🧠 BRAIN MEMORY (after load):")
cur.execute("SELECT key FROM system_memory")
for r in cur.fetchall():
    print(f"  - {r[0]}")

conn.close()
print("\n✅ ALL CONVERSATIONS LOADED INTO BRAIN!")
