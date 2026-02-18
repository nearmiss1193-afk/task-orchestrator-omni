"""Quick script: Update Clear Cut Tree Masters to interested + schedule 3:45 PM reminder"""
import os, json, time, threading, subprocess
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])

# 1. Find the lead
r = sb.table('contacts_master').select('id,company_name,status,ai_strategy').ilike('phone', '%8635832461%').execute()

if r.data:
    lead = r.data[0]
    print(f"Found: {lead['company_name']} (id={lead['id']}, status={lead['status']})")
    
    # Update status to interested
    strategy = lead.get('ai_strategy') or '{}'
    if isinstance(strategy, str):
        try: strategy = json.loads(strategy)
        except: strategy = {}
    
    strategy['callback'] = '2026-02-18T16:00:00-05:00'
    strategy['callback_type'] = 'discovery_call'
    strategy['notes'] = 'Owner replied sure to SMS. Dan spoke with him. Wants callback at 4pm EST 2/18.'
    strategy['priority'] = 'urgent'
    
    sb.table('contacts_master').update({
        'status': 'interested',
        'ai_strategy': json.dumps(strategy)
    }).eq('id', lead['id']).execute()
    
    print("DONE: Status -> interested, callback logged for 4pm")
else:
    # Not in DB yet, insert fresh
    print("Lead not in Supabase yet, inserting...")
    sb.table('contacts_master').insert({
        'company_name': 'Clear Cut Tree Masters',
        'phone': '+18635832461',
        'full_name': 'Owner',
        'niche': 'Tree Trimming',
        'status': 'interested',
        'source': 'lakeland_finds',
        'lead_source': 'lakeland_finds_directory',
        'ghl_contact_id': 'lkld_clearcut_tree',
        'ai_strategy': json.dumps({
            'callback': '2026-02-18T16:00:00-05:00',
            'callback_type': 'discovery_call',
            'notes': 'Owner replied sure to SMS. Dan spoke with him. Wants callback at 4pm EST 2/18.',
            'priority': 'urgent'
        })
    }).execute()
    print("DONE: Inserted as interested with 4pm callback")

# 2. Schedule 3:45 PM reminder via Windows Task Scheduler
print("\nSetting up 3:45 PM reminder...")
task_name = "ClearCutCallback345"

# Create the reminder command
reminder_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <TimeTrigger>
      <StartBoundary>2026-02-18T15:45:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('CALLBACK IN 15 MIN!`n`nClear Cut Tree Masters`n(863) 583-2461`nDiscovery Call at 4:00 PM`n`nTree Trimming - Lakeland FL', 'CALLBACK REMINDER', 'OK', 'Warning')"</Arguments>
    </Exec>
  </Actions>
  <Settings>
    <DeleteExpiredTaskAfterRunning>PT0S</DeleteExpiredTaskAfterRunning>
  </Settings>
</Task>'''

# Simpler approach: use schtasks
try:
    result = subprocess.run([
        'schtasks', '/create', '/tn', task_name, '/tr',
        'powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'CALLBACK IN 15 MIN! Clear Cut Tree Masters (863) 583-2461 - Discovery Call at 4:00 PM\', \'CALLBACK REMINDER\', \'OK\', \'Warning\')"',
        '/sc', 'once', '/st', '15:45', '/sd', '02/18/2026', '/f'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("DONE: Windows reminder set for 3:45 PM")
        print("  A popup will appear at 3:45 PM reminding you about the 4 PM call")
    else:
        print(f"schtasks error: {result.stderr}")
        print("FALLBACK: Set a manual alarm for 3:45 PM")
except Exception as e:
    print(f"Reminder setup error: {e}")
    print("FALLBACK: Set a manual alarm for 3:45 PM")
