"""Email Performance Report — Real opens vs Dan's test opens"""
from supabase import create_client
import os, json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from collections import Counter
load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

dan_emails = ['owner@aiserviceco.com', 'nearmiss1193@gmail.com']

# Get all email touches (paginate if needed)
all_data = []
offset = 0
while True:
    batch = sb.table('outbound_touches').select(
        'id,channel,status,variant_id,variant_name,payload,ts,company'
    ).eq('channel', 'email').order('ts', desc=True).range(offset, offset + 999).execute()
    all_data.extend(batch.data)
    if len(batch.data) < 1000:
        break
    offset += 1000

total = len(all_data)
print('=== EMAIL PERFORMANCE REPORT ===')
print('Total emails sent:', total)
print()

# Status breakdown
statuses = Counter(t.get('status', 'unknown') for t in all_data)
print('Status breakdown:')
for s, c in statuses.most_common():
    print('  %s: %d' % (s, c))
print()

# Separate Dan's emails from real leads
real_opens = []
dan_opens = []
real_sent = 0
real_delivered = 0

for t in all_data:
    p = t.get('payload') or {}
    to_email = str(p.get('to', '') or '').lower()
    events = p.get('events', []) if isinstance(p.get('events'), list) else []
    is_dan = to_email in dan_emails

    has_open = any(e.get('type') == 'email.opened' for e in events if isinstance(e, dict))

    if is_dan:
        if has_open:
            dan_opens.append(t)
    else:
        real_sent += 1
        if t.get('status') in ['delivered', 'opened', 'clicked']:
            real_delivered += 1
        if has_open:
            real_opens.append(t)

print('--- REAL LEADS (excluding Dan) ---')
print('Emails to real leads:', real_sent)
print('Delivered:', real_delivered)
print('Opened by REAL leads:', len(real_opens))
if real_sent > 0:
    print('Open rate: %.1f%%' % (len(real_opens)/real_sent*100))
print('Opened by Dan (test):', len(dan_opens))
print()

# Show real opens
if real_opens:
    print('=== REAL OPENS (leads who opened your email) ===')
    for t in real_opens[:20]:
        p = t.get('payload') or {}
        co = str(t.get('company', '?'))
        to = str(p.get('to', '?'))
        vid = str(t.get('variant_id', '?'))
        ts = str(t.get('ts', ''))[:10]
        print('  %s | %s | variant: %s | sent: %s' % (co, to, vid, ts))
    print()
else:
    print('No real opens recorded yet.')
    print('(Webhook was just configured — opens will start appearing as leads read emails)')
    print()

# Check tracking pixel opens (from our custom pixel)
print('--- TRACKING PIXEL OPENS (from our embedded pixel) ---')
tracking_touches = sb.table('outbound_touches').select(
    'id,company,payload,ts'
).eq('channel', 'email').eq('status', 'opened').order('ts', desc=True).limit(20).execute()
pixel_opens = 0
for t in tracking_touches.data:
    p = t.get('payload') or {}
    to_email = str(p.get('to', '') or '').lower()
    if to_email not in dan_emails:
        co = str(t.get('company', '?'))
        ts = str(t.get('ts', ''))[:16]
        print('  %s | %s | %s' % (co, to_email, ts))
        pixel_opens += 1
print('Total pixel-tracked opens (not Dan):', pixel_opens)
print()

# Bounces
bounced = [t for t in all_data if t.get('status') == 'bounced']
print('Bounced: %d' % len(bounced))
if bounced:
    for t in bounced[:10]:
        p = t.get('payload') or {}
        print('  %s | %s' % (t.get('company','?'), p.get('to','?')))
print()

# A/B performance
print('=== A/B SUBJECT LINE PERFORMANCE ===')
variant_stats = {}
for t in all_data:
    p = t.get('payload') or {}
    to_email = str(p.get('to', '') or '').lower()
    if to_email in dan_emails:
        continue
    vid = str(t.get('variant_id', '?'))
    vname = str(t.get('variant_name', ''))
    if vid not in variant_stats:
        variant_stats[vid] = {'name': vname, 'sent': 0, 'opened': 0}
    variant_stats[vid]['sent'] += 1
    events = p.get('events', []) if isinstance(p.get('events'), list) else []
    if any(e.get('type') == 'email.opened' for e in events if isinstance(e, dict)):
        variant_stats[vid]['opened'] += 1
    if t.get('status') == 'opened':
        variant_stats[vid]['opened'] += 1

for vid, s in sorted(variant_stats.items(), key=lambda x: x[1]['sent'], reverse=True):
    rate = '%.1f%%' % (s['opened']/s['sent']*100) if s['sent'] > 0 else '0%'
    name = s['name'][:60]
    print('  %s: %d sent, %d opened (%s) | %s' % (vid, s['sent'], s['opened'], rate, name))
print()

# Timeline
print('=== SEND TIMELINE ===')
by_day = Counter()
for t in all_data:
    p = t.get('payload') or {}
    to_email = str(p.get('to', '') or '').lower()
    if to_email not in dan_emails:
        day = str(t.get('ts', ''))[:10]
        if day:
            by_day[day] += 1
for day, count in sorted(by_day.items()):
    print('  %s: %d emails' % (day, count))
