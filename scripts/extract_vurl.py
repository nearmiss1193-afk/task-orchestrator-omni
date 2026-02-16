
import json
from modules.database.supabase_client import get_supabase

def run():
    sb = get_supabase()
    res = sb.table('contacts_master').select('company_name,raw_research').eq('status', 'research_done').limit(5).execute()
    for l in res.data:
        raw = l.get('raw_research')
        if not raw: continue
        if isinstance(raw, str): raw = json.loads(raw)
        vurl = raw.get('video_teaser_url')
        if vurl:
            print(f"Post Link: {vurl}")
            print(f"Company: {l['company_name']}")
            return

if __name__ == "__main__":
    run()
