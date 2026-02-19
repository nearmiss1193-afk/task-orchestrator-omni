import json, sys

d = json.load(open('stats_v7.txt'))
with open('analysis_clean.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("OUTREACH STATUS CHECK\n")
    f.write("=" * 60 + "\n")
    f.write(f"Outbound last 24h: {d['outbound_24h']}\n\n")

    f.write("LAST 5 OUTBOUND TOUCHES:\n")
    for a in d['activity'][:5]:
        ts = a.get('ts','?')[:19]
        ch = a.get('channel','?')
        st = a.get('status','?')
        f.write(f"  {ts}  {ch:8s}  {st}\n")
    f.write("\n")

    f.write("LEAD FUNNEL:\n")
    fn = d.get('funnel', {})
    for k in ['total','new','research_done','outreach_sent','responded','customer','bounced','bad_email']:
        f.write(f"  {k:20s}: {fn.get(k, '?')}\n")
    f.write("\n")

    f.write("SYSTEM HEALTH:\n")
    h = d.get('health', {})
    hb = h.get('last_heartbeat','None')
    f.write(f"  Status:          {h.get('status')}\n")
    f.write(f"  Heartbeat OK:    {h.get('heartbeat_ok')}\n")
    f.write(f"  Last heartbeat:  {hb[:19] if hb and hb != 'None' else 'None'}\n\n")

    f.write("A/B EMAIL PERFORMANCE (7d):\n")
    for v in d.get('ab_performance', []):
        f.write(f"  {v.get('variant','?')}: sent={v.get('sent',0)} opened={v.get('opened',0)} replied={v.get('replied',0)} open_rate={v.get('open_rate',0)}%\n")
    f.write("\n")

    f.write("STRIPE:\n")
    s = d.get('stripe', {})
    f.write(f"  MRR: ${s.get('mrr', 0)}\n")
    f.write(f"  Active subs: {s.get('active_subs', 0)}\n")
    f.write(f"  Revenue 30d: ${s.get('total_revenue_30d', 0)}\n")
    if s.get('error'):
        f.write(f"  Error: {s['error']}\n")
    f.write("\n")

    f.write("LEAD GEO (top 5):\n")
    for g in d.get('lead_geo', [])[:5]:
        f.write(f"  {g.get('city','?'):20s}: {g.get('count',0)}\n")

print("Done - wrote analysis_clean.txt")
