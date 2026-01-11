import json

with open('todays_transcripts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total = len(data)
with_transcript = [c for c in data if c.get('transcript', '').strip()]
human_contact = [c for c in data if 'User:' in c.get('transcript', '')]
answered_calls = [c for c in data if c.get('ended_reason') in ['customer-ended-call', 'assistant-ended-call', 'silence-timed-out'] and c.get('transcript')]

print(f"📊 CALL ANALYSIS")
print(f"=" * 50)
print(f"Total calls today: {total}")
print(f"Calls with transcripts: {len(with_transcript)}")
print(f"Human contact made: {len(human_contact)}")
print(f"Answered (not failed): {len(answered_calls)}")
print()

# Breakdown by end reason
reasons = {}
for call in data:
    reason = call.get('ended_reason', 'unknown')
    reasons[reason] = reasons.get(reason, 0) + 1

print("End Reasons:")
for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
    print(f"  {reason}: {count}")

print()
print("Sample Conversations with Humans:")
print("=" * 50)
for i, call in enumerate(human_contact[:5]):
    print(f"\n{i+1}. {call['customer_name']} - {call.get('ended_reason', 'N/A')}")
    transcript = call.get('transcript', '')[:300]
    print(f"   {transcript}...")
