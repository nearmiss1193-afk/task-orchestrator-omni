"""Diagnose call hangup and SMS issues"""
import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

print("="*60)
print("CALL DIAGNOSIS")
print("="*60)

# Get recent calls
r = requests.get('https://api.vapi.ai/call?limit=5', headers=headers)
calls = r.json()

for c in calls[:3]:
    print(f"\nCall: {c.get('id','?')[:16]}...")
    print(f"  Type: {c.get('type')}")
    print(f"  Status: {c.get('status')}")
    print(f"  Ended Reason: {c.get('endedReason')}")
    print(f"  Duration: {c.get('duration',0)}s")
    print(f"  Time: {c.get('createdAt','?')[:19]}")

# Get full details of latest call
if calls:
    call_id = calls[0].get('id')
    print(f"\n{'='*60}")
    print(f"LATEST CALL FULL DETAILS ({call_id[:12]}...):")
    print("="*60)
    
    # Get transcript if available
    transcript = calls[0].get('transcript', 'No transcript')
    print(f"Transcript: {transcript[:500] if transcript else 'None'}")
    
    analysis = calls[0].get('analysis', {})
    if analysis:
        print(f"\nAnalysis Summary: {analysis.get('summary', 'N/A')}")

print("\n" + "="*60)
print("SMS DIAGNOSIS")
print("="*60)
print("NOTE: SMS is handled by GHL, NOT Vapi!")
print("Inbound SMS to GHL number goes to GHL Conversations")
print("AI response requires GHL AI agent configuration or custom webhook")
print("="*60)
