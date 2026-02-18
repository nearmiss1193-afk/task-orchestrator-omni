"""
Lakeland Expansion Round 2 - Get remaining ~1,100 businesses to hit 5,500+
Uses more specific/niche search terms and expanded geographic radius.
"""
import os, csv, json, time, requests, re
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

GOOGLE_KEY = "AIzaSyBGk4aUs49p5D7OoB4Sn0AoYMqGL9VcP7A"

# Load ALL existing place_ids (original 3,321 + expansion 1,056)
existing_ids = set()
for csvfile in ['lakeland_businesses_enriched.csv', 'lakeland_expansion.csv']:
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), csvfile)
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row.get('place_id', '').strip()
                if pid: existing_ids.add(pid)
                key = f"{row.get('name','')}-{row.get('address','')}"
                existing_ids.add(key)

print(f"Total existing IDs to dedup against: {len(existing_ids)}")

# Round 2 search terms - more granular categories + wider geographic area
SEARCH_TERMS_R2 = [
    # Deeper Lakeland niches not yet covered
    "cleaning service Lakeland FL",
    "janitorial Lakeland FL",
    "security company Lakeland FL",
    "alarm system Lakeland FL",
    "surveillance Lakeland FL",
    "photography studio Lakeland FL",
    "videographer Lakeland FL",
    "graphic design Lakeland FL",
    "web developer Lakeland FL",
    "tax preparation Lakeland FL",
    "notary Lakeland FL",
    "real estate Lakeland FL",
    "property management Lakeland FL",
    "apartment complex Lakeland FL",
    "storage unit Lakeland FL",
    "self storage Lakeland FL",
    "gas station Lakeland FL",
    "convenience store Lakeland FL",
    "tobacco shop Lakeland FL",
    "smoke shop Lakeland FL",
    "liquor store Lakeland FL",
    "dry cleaner Lakeland FL",
    "tailor Lakeland FL",
    "seamstress Lakeland FL",
    "upholstery Lakeland FL",
    "carpet store Lakeland FL",
    "tile store Lakeland FL",
    "paint store Lakeland FL",
    "lumber yard Lakeland FL",
    "welding shop Lakeland FL",
    "machine shop Lakeland FL",
    "manufacturing Lakeland FL",
    "warehouse Lakeland FL",
    "shipping company Lakeland FL",
    "trucking company Lakeland FL",
    "courier service Lakeland FL",
    "printing company Lakeland FL",
    "packaging supply Lakeland FL",
    "office supply Lakeland FL",
    "electronics store Lakeland FL",
    "appliance store Lakeland FL",
    "pool supply Lakeland FL",
    "aquarium store Lakeland FL",
    "feed store Lakeland FL",
    "tractor supply Lakeland FL",
    "farm equipment Lakeland FL",
    "horse boarding Lakeland FL",
    "veterinary clinic Lakeland FL",
    "animal shelter Lakeland FL",
    "travel agency Lakeland FL",
    "hotel Lakeland FL",
    "motel Lakeland FL",
    "bed and breakfast Lakeland FL",
    "campground Lakeland FL",
    "RV park Lakeland FL",
    # Wider geographic radius - specific niches
    "restaurant Plant City FL",
    "hair salon Plant City FL",
    "dentist Plant City FL",
    "auto repair Plant City FL",
    "lawyer Plant City FL",
    "doctor Plant City FL",
    "pharmacy Plant City FL",
    "gym Plant City FL",
    "church Plant City FL",
    "daycare Plant City FL",
    "restaurant Mulberry FL",
    "store Mulberry FL",
    "services Mulberry FL",
    "restaurant Haines City FL",
    "store Haines City FL",
    "services Haines City FL",
    "restaurant Davenport FL",
    "store Davenport FL",
    "services Davenport FL",
    "restaurant Dundee FL",
    "store Dundee FL",
    "restaurant Eagle Lake FL",
    "restaurant Lake Wales FL",
    "store Lake Wales FL",
    "services Lake Wales FL",
    "restaurant Frostproof FL",
    "restaurant Avon Park FL",
    "store Avon Park FL",
    "restaurant Sebring FL",
    "store Sebring FL",
    "restaurant Lake Alfred FL",
    "restaurant Zephyrhills FL",
    "store Zephyrhills FL",
    "services Zephyrhills FL",
    "restaurant Dade City FL",
    "store Dade City FL",
    # Broad area searches
    "new business Polk County FL",
    "small business Polk County FL",
    "business near 33801",
    "business near 33803",
    "business near 33805",
    "business near 33809",
    "business near 33810",
    "business near 33811",
    "business near 33813",
    "business near 33815",
    "business near 33880",  # Winter Haven
    "business near 33830",  # Bartow
    "business near 33566",  # Plant City
    "business near 33844",  # Haines City
    "business near 33837",  # Davenport
    "business near 33853",  # Lake Wales
    # Highly specific
    "nail salon Bartow FL",
    "barber Bartow FL",
    "pizza Winter Haven FL",
    "Mexican food Winter Haven FL",
    "Chinese food Bartow FL",
    "insurance Winter Haven FL",
    "car wash Winter Haven FL",
    "tire shop Bartow FL",
    "pawn shop Winter Haven FL",
    "thrift store Bartow FL",
    "church Bartow FL",
    "church Winter Haven FL",
    "church Auburndale FL",
    "gym Bartow FL",
    "gym Winter Haven FL",
    "pet grooming Winter Haven FL",
    "florist Bartow FL",
    "bakery Winter Haven FL",
    "coffee shop Bartow FL",
    "ice cream Winter Haven FL",
    "cell phone repair Winter Haven FL",
    "tattoo shop Bartow FL",
    "spa Winter Haven FL",
    "massage Bartow FL",
]

def search_places(query, page_token=None):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_KEY}
    if page_token:
        params = {"pagetoken": page_token, "key": GOOGLE_KEY}
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    if data.get("status") not in ["OK", "ZERO_RESULTS"]:
        print(f"  API Error: {data.get('status')} - {data.get('error_message','')[:80]}")
    return data.get("results", []), data.get("next_page_token")

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": "formatted_phone_number,website", "key": GOOGLE_KEY}
    r = requests.get(url, params=params, timeout=15)
    result = r.json().get("result", {})
    return {"phone": result.get("formatted_phone_number", ""), "website": result.get("website", "")}

def main():
    new_biz = []
    seen = set(existing_ids)
    api_calls = 0
    
    for i, q in enumerate(SEARCH_TERMS_R2):
        print(f"\n[{i+1}/{len(SEARCH_TERMS_R2)}] {q}")
        try:
            results, nxt = search_places(q)
            api_calls += 1
            for r in results:
                pid = r.get("place_id","")
                name = r.get("name","")
                addr = r.get("formatted_address","")
                key = f"{name}-{addr}"
                if pid in seen or key in seen: continue
                seen.add(pid); seen.add(key)
                types = r.get("types",[])
                cat = types[0].replace("_"," ").title() if types else q.split(" near ")[0].split(" FL")[0].strip()
                new_biz.append({"name":name,"address":addr,"category":cat,"phone":"","website":"","email":"","rating":r.get("rating",""),"total_ratings":r.get("user_ratings_total",""),"place_id":pid})
            
            print(f"  Page 1: {len(results)} results, {len(new_biz)} total new")
            
            for pg in [2,3]:
                if not nxt: break
                time.sleep(2)
                results, nxt = search_places(q, nxt)
                api_calls += 1
                for r in results:
                    pid = r.get("place_id","")
                    name = r.get("name","")
                    addr = r.get("formatted_address","")
                    key = f"{name}-{addr}"
                    if pid in seen or key in seen: continue
                    seen.add(pid); seen.add(key)
                    types = r.get("types",[])
                    cat = types[0].replace("_"," ").title() if types else q.split(" near ")[0].split(" FL")[0].strip()
                    new_biz.append({"name":name,"address":addr,"category":cat,"phone":"","website":"","email":"","rating":r.get("rating",""),"total_ratings":r.get("user_ratings_total",""),"place_id":pid})
                print(f"  Page {pg}: {len(results)} results, {len(new_biz)} total new")
            
            if len(new_biz) >= 1500:
                print(f"\nHIT TARGET: {len(new_biz)} new!")
                break
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"R2 SEARCH COMPLETE: {len(new_biz)} new businesses, {api_calls} API calls")
    
    # Fetch phone details
    print(f"\nFetching phone details...")
    phone_count = 0
    for j, b in enumerate(new_biz):
        try:
            d = get_place_details(b["place_id"])
            b["phone"] = d["phone"]
            b["website"] = d["website"]
            api_calls += 1
            if d["phone"]: phone_count += 1
            if (j+1) % 100 == 0:
                print(f"  {j+1}/{len(new_biz)} | phones: {phone_count}")
            time.sleep(0.1)
        except: continue
    
    # Save
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lakeland_expansion_r2.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['name','address','category','phone','website','email','rating','total_ratings','place_id'])
        w.writeheader()
        w.writerows(new_biz)
    
    # Merge all three CSVs into one master
    all_biz = []
    for csvf in ['lakeland_businesses_enriched.csv', 'lakeland_expansion.csv', 'lakeland_expansion_r2.csv']:
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), csvf)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                all_biz.extend(list(csv.DictReader(f)))
    
    master = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lakeland_master_5500.csv')
    with open(master, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['name','address','category','phone','website','email','rating','total_ratings','place_id'])
        w.writeheader()
        w.writerows(all_biz)
    
    summary = f"""R2 EXPANSION RESULTS:
New businesses (R2): {len(new_biz)}
With phone (R2): {phone_count}
API calls (R2): {api_calls}
COMBINED TOTAL: {len(all_biz)}
Master CSV: {master}
"""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expansion_r2_result.txt'), 'w') as f:
        f.write(summary)
    print(f"\n{summary}")

if __name__ == "__main__":
    main()
