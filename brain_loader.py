"""
brain_loader.py - Load ALL historical data into Brain memory
Aggregates: conversations, tasks, actions, successes, failures, knowledge
"""
import os
import json
import glob
import psycopg2
from datetime import datetime

# Direct DB connection
DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

BRAIN_DIR = r'C:\Users\nearm\.gemini\antigravity\brain'
KNOWLEDGE_DIR = r'C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\knowledge_base'

def load_file_content(filepath, max_chars=5000):
    """Read file content with size limit"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()[:max_chars]
    except Exception as e:
        return f"Error reading: {e}"

def aggregate_conversations():
    """Aggregate all conversation artifacts"""
    print("\n📚 LOADING CONVERSATIONS...")
    conversations = []
    
    for conv_dir in glob.glob(os.path.join(BRAIN_DIR, '*/')):
        conv_id = os.path.basename(conv_dir.rstrip('/\\'))
        if len(conv_id) < 30:  # Skip non-UUID directories
            continue
            
        # Look for key artifacts
        artifacts = {
            'task_md': os.path.join(conv_dir, 'task.md'),
            'implementation_plan': os.path.join(conv_dir, 'implementation_plan.md'),
            'walkthrough': os.path.join(conv_dir, 'walkthrough.md'),
        }
        
        conv_data = {'id': conv_id, 'files': []}
        for name, path in artifacts.items():
            if os.path.exists(path):
                content = load_file_content(path, 3000)
                conv_data['files'].append({
                    'name': name,
                    'content': content[:2000]  # Limit per file
                })
        
        if conv_data['files']:
            conversations.append(conv_data)
            print(f"  ✓ {conv_id[:8]}... ({len(conv_data['files'])} files)")
    
    return conversations

def aggregate_knowledge_base():
    """Aggregate all knowledge base files"""
    print("\n📖 LOADING KNOWLEDGE BASE...")
    knowledge = []
    
    for md_file in glob.glob(os.path.join(KNOWLEDGE_DIR, '*.md')):
        filename = os.path.basename(md_file)
        content = load_file_content(md_file, 4000)
        knowledge.append({
            'name': filename,
            'content': content
        })
        print(f"  ✓ {filename}")
    
    return knowledge

def extract_learnings(conversations):
    """Extract key learnings from conversation artifacts"""
    learnings = []
    
    # Pattern matching for successes and failures
    success_keywords = ['✅', 'success', 'complete', 'fixed', 'deployed', 'working']
    failure_keywords = ['❌', 'failed', 'error', 'bug', 'issue', 'blocked']
    
    for conv in conversations:
        for file_data in conv['files']:
            content = file_data['content'].lower()
            
            # Extract successes
            for kw in success_keywords:
                if kw in content:
                    learnings.append({
                        'type': 'success',
                        'source': f"{conv['id'][:8]}/{file_data['name']}",
                        'keyword': kw
                    })
                    break
            
            # Extract failures
            for kw in failure_keywords:
                if kw in content:
                    learnings.append({
                        'type': 'failure', 
                        'source': f"{conv['id'][:8]}/{file_data['name']}",
                        'keyword': kw
                    })
                    break
    
    return learnings

def save_to_brain(conversations, knowledge, learnings):
    """Save aggregated data to system_memory"""
    print("\n💾 SAVING TO BRAIN DATABASE...")
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Ensure table exists with proper schema
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create agent_learnings if needed
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_learnings (
                id SERIAL PRIMARY KEY,
                agent_name TEXT,
                topic TEXT,
                insight TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Save conversation summaries
        conv_summary = json.dumps([{
            'id': c['id'][:8],
            'files': len(c['files'])
        } for c in conversations])
        
        cur.execute("""
            INSERT INTO system_memory (key, value, created_at) 
            VALUES ('conversation_history', %s, NOW())
            ON CONFLICT (key) DO UPDATE SET value = %s, created_at = NOW()
        """, (conv_summary, conv_summary))
        print(f"  ✓ Saved {len(conversations)} conversation summaries")
        
        # Save knowledge base index
        kb_summary = json.dumps([k['name'] for k in knowledge])
        cur.execute("""
            INSERT INTO system_memory (key, value, created_at)
            VALUES ('knowledge_base_index', %s, NOW())
            ON CONFLICT (key) DO UPDATE SET value = %s, created_at = NOW()
        """, (kb_summary, kb_summary))
        print(f"  ✓ Indexed {len(knowledge)} knowledge files")
        
        # Save each knowledge file content
        for kb in knowledge:
            key = f"kb_{kb['name'].replace('.md', '')}"
            cur.execute("""
                INSERT INTO system_memory (key, value, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (key) DO UPDATE SET value = %s, created_at = NOW()
            """, (key, kb['content'][:4000], kb['content'][:4000]))
        print(f"  ✓ Stored {len(knowledge)} knowledge base contents")
        
        # Save learnings summary
        success_count = len([l for l in learnings if l['type'] == 'success'])
        failure_count = len([l for l in learnings if l['type'] == 'failure'])
        
        learnings_summary = json.dumps({
            'total_conversations': len(conversations),
            'successes': success_count,
            'failures': failure_count,
            'last_updated': datetime.now().isoformat()
        })
        
        cur.execute("""
            INSERT INTO system_memory (key, value, created_at)
            VALUES ('meta_learnings', %s, NOW())
            ON CONFLICT (key) DO UPDATE SET value = %s, created_at = NOW()
        """, (learnings_summary, learnings_summary))
        print(f"  ✓ Recorded {success_count} successes, {failure_count} failures")
        
        # Save master system prompt context
        master_context = f"""
# Empire Brain Context
Last Updated: {datetime.now().isoformat()}

## Conversation History
- {len(conversations)} past conversations analyzed
- Key artifacts: task.md, implementation_plan.md, walkthrough.md

## Knowledge Base ({len(knowledge)} files)
{', '.join([k['name'] for k in knowledge])}

## Learnings
- {success_count} successful operations
- {failure_count} failure patterns identified

## Key Capabilities
- Pricing: $297/$497/$997 (Golden Standard)
- Trial: 14-Day Free Trial
- AI: Sarah the Spartan (Vapi voice)
- Dashboard: Empire Mission Control v2.3
- Leads: 139 in pipeline

## Common Issues to Avoid
- .env null character corruption
- GitHub GH013 secret scanning blocks
- Vapi call forwarding is phone-level not assistant-level
- Dashboard shows 0 when Supabase connection fails
"""
        
        cur.execute("""
            INSERT INTO system_memory (key, value, created_at)
            VALUES ('master_context', %s, NOW())
            ON CONFLICT (key) DO UPDATE SET value = %s, created_at = NOW()
        """, (master_context, master_context))
        print("  ✓ Saved master context")
        
        conn.commit()
        conn.close()
        
        print("\n✅ BRAIN LOADING COMPLETE!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧠 EMPIRE BRAIN LOADER")
    print("   Loading all historical data for continuous improvement")
    print("=" * 60)
    
    # Aggregate all data
    conversations = aggregate_conversations()
    knowledge = aggregate_knowledge_base()
    learnings = extract_learnings(conversations)
    
    # Save to brain
    success = save_to_brain(conversations, knowledge, learnings)
    
    # Final report
    print("\n" + "=" * 60)
    print("📊 BRAIN LOAD SUMMARY")
    print(f"   Conversations: {len(conversations)}")
    print(f"   Knowledge Files: {len(knowledge)}")
    print(f"   Learnings Extracted: {len(learnings)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
