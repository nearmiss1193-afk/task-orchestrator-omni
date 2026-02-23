"""
ABACUS.AI AUTO-TRIAGE DAEMON
Instructions: Paste this entire script into a new Python feature group or scheduled Deployment inside Abacus.AI. 

This daemon connects to your Neon Postgres database, scans the `outbound_touches` and `contacts_master` tables, and uses Abacus LLMs to "Auto-Tag" leads based on sentiment (e.g., "Ready to Buy", "Needs Human Intervention"). The Next.js C2 Dashboard will instantly read these tags.
"""

import os
import json
import psycopg2
from abacusai import ApiClient

# ==========================================
# 1. CREDENTIALS AND CONFIGURATION
# ==========================================
# Securely inject the Neon/Supabase Postgres connection via Abacus Feature Group Secrets
DATABASE_URL = os.environ.get("SUPABASE_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("CRITICAL SECURITY ERROR: SUPABASE_DATABASE_URL Secret is not set in the Abacus Environment.")

# Initialize Abacus Client (Abacus auto-injects credentials in its own environment)
client = ApiClient() 

def analyze_sentiment(lead_history):
    """
    Calls an Abacus LLM to determine the sentiment of the conversation.
    """
    prompt = f"""
    You are an expert sales triage AI. Analyze the following conversation history with a lead.
    Determine the current status of the lead. Reply ONLY with one of the following exact JSON strings:
    {{"tag": "Needs Human Intervention", "color": "red"}}
    {{"tag": "Ready to Buy", "color": "green"}}
    {{"tag": "Not Interested", "color": "gray"}}
    {{"tag": "Auto-Nurturing", "color": "blue"}}

    Conversation History:
    {lead_history}
    """
    
    # Execute prompt against Abacus hosted LLM (e.g., Llama 3 or GPT-4 integrated via Abacus)
    try:
        # Note: Adjust the model name to your specific Abacus hosted LLM deployment ID
        response = client.evaluate_prompt(prompt=prompt, model="default")
        return json.loads(response.content)
    except Exception as e:
        print(f"Abacus LLM Error: {e}")
        return {"tag": "Needs Human Intervention", "color": "red"}

def run_triage_sweep():
    print("Initiating Abacus C2 Triage Sweep...")
    
    # Connect directly to Sovereign Empire Database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 1. Find leads that have replied recently but haven't been tagged
    cursor.execute("""
        SELECT lead_id, phone, email 
        FROM outbound_touches 
        WHERE status = 'replied' AND ts > NOW() - INTERVAL '24 hours'
        GROUP BY lead_id, phone, email;
    """)
    active_leads = cursor.fetchall()
    
    print(f"Found {len(active_leads)} active conversations to analyze.")
    
    for lead in active_leads:
        lead_id, phone, email = lead
        identifier_clause = f"phone = '{phone}'" if phone else f"email = '{email}'"
        
        # Pull the last 5 messages for context
        cursor.execute(f"""
            SELECT direction, body, ts 
            FROM outbound_touches 
            WHERE {identifier_clause} 
            ORDER BY ts DESC LIMIT 5;
        """)
        history = cursor.fetchall()
        
        # Format history for the LLM
        formatted_history = "\n".join([f"[{row[0].upper()}] {row[2]}: {row[1]}" for row in history])
        
        # 2. Ask Abacus LLM to analyze the conversation
        analysis = analyze_sentiment(formatted_history)
        tag_json = json.dumps(analysis)
        
        # 3. Write the intelligence tag back to the contacts_master table 
        # (The Next.js C2 dashboard will read this column)
        try:
            # We assume a column 'abacus_tags' exists or we use 'notes' temporarily
            cursor.execute(f"""
                UPDATE contacts_master 
                SET notes = CONCAT(notes, '\n[ABACUS TRIAGE]: ', '{tag_json}')
                WHERE id = '{lead_id}';
            """)
            conn.commit()
            print(f"Successfully tagged Lead {lead_id}: {analysis['tag']}")
        except Exception as e:
            print(f"Database write error for lead {lead_id}: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
    print("Abacus Sweep Complete.")

if __name__ == "__main__":
    run_triage_sweep()
