"""Save critical config to Supabase memory"""
from supabase import create_client

url = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'

sb = create_client(url, key)

# Critical config to store
configs = [
    {'key': 'ghl_form_id', 'status': '7TTJ1CUAFjhON69ZsOZK', 'notes': 'CORRECT form ID - links.aiserviceco.com'},
    {'key': 'ghl_calendar_id', 'status': 'YWQcHuXXznQEQa7LAWeB', 'notes': 'CORRECT calendar ID - links.aiserviceco.com'},
    {'key': 'ghl_embed_domain', 'status': 'links.aiserviceco.com', 'notes': 'NOT api.leadconnectorhq.com or link.msgsndr.com'},
    {'key': 'vapi_public_key', 'status': '3b065ff0-a721-4b66-8255-30b6b8d6daab', 'notes': 'Vapi widget API key'},
    {'key': 'vapi_assistant_id', 'status': '1a797f12-e2dd-4f7f-b2c5-08c38c74859a', 'notes': 'Sarah assistant ID'},
    {'key': 'vapi_widget_style', 'status': 'pill', 'notes': 'Talk to Sales, Ask anything, mic icon, #f59e0b yellow'},
]

for cfg in configs:
    try:
        result = sb.table('system_state').upsert(cfg, on_conflict='key').execute()
        print(f"Saved: {cfg['key']} = {cfg['status']}")
    except Exception as e:
        print(f"Error saving {cfg['key']}: {e}")

print("\n=== MEMORY SAVED TO SUPABASE ===")
