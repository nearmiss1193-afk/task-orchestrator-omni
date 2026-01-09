import os
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def run_cortex_loop():
    print("🧠 Cortex Loop Initiated...")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. ANALYZE: Fetch basic stats
        cur.execute("SELECT count(*) FROM leads;")
        lead_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM call_transcripts;")
        call_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM system_logs WHERE level = 'ERROR';")
        error_count = cur.fetchone()[0]

        # 2. SYNTHESIZE: Create a new Operational Buffer
        # In a real scenario, this would use an LLM to summarize recent logs.
        # For now, we construct a structured status update.
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        status_message = f"""
# 🧠 CORTEX STATUS UPDATE [{timestamp}]

## 📊 SYSTEM METRICS
- **Leads Tracked**: {lead_count}
- **Neural Interventions (Calls)**: {call_count}
- **System Anomalies**: {error_count}

## 🛡️ ACTIVE DIRECTIVES
1.  **Monitor**: Keep finding leads. 
2.  **Optimize**: Refine email scripts based on reply rates.
3.  **Expand**: Prepare for multi-agent swarm deployment.

## ⚠️ ALERTS
- Check error logs if Anomalies > 0.
- Ensure Vapi balance is sufficient.

> "Growth is the only evidence of life." - Sovereign System
"""

        print("📝 Generated New Memory Buffer:")
        print(status_message)

        # 2b. ENSURE TABLE EXISTS
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # 3. UPDATE: Push to System Memory
        upsert_query = """
        INSERT INTO system_memory (key, value, created_at)
        VALUES ('operational_buffer', %s, NOW())
        ON CONFLICT (key) 
        DO UPDATE SET value = EXCLUDED.value, created_at = NOW();
        """
        
        cur.execute(upsert_query, (status_message,))
        conn.commit()
        
        print("✅ Operational Memory Synced.")

        conn.close()

    except Exception as e:
        print(f"❌ Cortex Error: {e}")

if __name__ == "__main__":
    run_cortex_loop()
