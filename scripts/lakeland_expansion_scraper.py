"""
Lakeland Business Expansion Scraper v2
Goal: Scrape ~2,200+ new businesses to bring total from 3,321 to 5,500+.

Strategy:
- Use Google Places Text Search API with pagination (3 pages x 20 = 60 per query)
- Cover NEW search terms not well-represented in current data
- Deduplicate against existing place_ids
- Save to expansion CSV
"""
import os, csv, json, time, requests, re
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Use the unrestricted API key 2 from Google Cloud Console
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in environment")
print(f"Google API Key: {str(GOOGLE_KEY)[:5]}...[SECURE]")

# Load already-contacted phone numbers (to exclude from voice drop CSV)
ALREADY_CONTACTED_PHONES = set()
already_contacted_raw = [
    "3212976079","8132671289","8132792727","4079304455","4077195944","4078847555",
    "8138554461","4073833659","4073833659","8139716100","4078860204","4073093165",
    "8132819079","3212561234","8134129333","4078802886","4075189355","8135087791",
    "8138554461","4076052888","4075180880","8135022755","8138753083","4076775400",
    "4072787858","4079606254","4077959250","8131107483","8139490424","4076477777",
    "4078788383","3216098870","7873101338","8132543206","4073356777","3523943318",
    "3523943318","8131067067","8137272159","8132659702","4074294364","8137984717",
    "4074364414","8134960407","8135039020","4074316795","4079576290","4074831182",
    "8136817183","4076729662","8132036001","4078870104","4078550388","8132072040",
    "4075745177","8134329111","8136509393","8139467711","8134521570","4078787387",
    "3213402590","7275156077","4072176969","8134905211","3527492459","8134942411",
    "8133139253","8131354904","4075202322","8133777321","8133777321","8133777321",
    "4072971077","4072971077","8135938128","8135938128","8138180600","8137601060",
    "4076969626","4076760076","4073486042","4074103200","4078634856","4073833301",
    "4076368178","6892991931","4072884813","3219262997","4073611860","4079791033",
    "8132653033","4079039444","4074238164","4074238164","4074238164","4079681801",
    "8133777321","4072971077","8138159280","8138452391","4075202322","4072726040",
    "4076283450","8137788206","4077100526","4079307309","3213607663","8136548686",
    "4078926617","4075749009","3213214520","4072037037","4075664646","4078463912",
    "3219392168","4076717974","4079102255","8139325511","4075189355","8139621121",
    "4072884672","8138910400","8883427314","8139973140","4072787858","4073073076",
    "7276773373","4075390639","8137496863","8138862506","4078035230","8132394685",
    "4078770333","4077018733","8138358900","8139492995","7867639677","8135473226",
    "4072098114","3108097109","8137752276","3214309621","3216243034","4078977050",
    "4076542316","8132704794","8134867285","4073601806","6898887911","4073198985",
    "8132326261","8132031764","4072035138","5719829312","8138867000","6893146219",
    "8136722500","4076630490","4073485607","4073618016","4076720001","4078513437",
    "8638040000","8338990310","8635333838","8635148077","8338990310","8638607633",
    "8636471515","8639400874","8638756817","8636983766","8636872287","8632209316",
    "8636482958","8632251950","8632585820","8635148077","8133249311","8638590335",
    "8636602185","8638081799","8632943360","8632254519","8636868151","8632327626",
    "8632327626","8636658231","4077772071","8636836511","8636074222","8635376408",
    "8634100041","7278230540","8132211154","8634220247","8636042357","8635331220",
    "8135163121","8632594743","8636668392","8638370530","8636566672","8632876388",
    "8633375013","8632131608","8639409950","8635294082","8632988026","7278230540",
    "8636837500","8636143819","8636659597","8636888834","8636763556","8635336698",
    "8636042357","8637974400","8638592837","8632686552"
]
for p in already_contacted_raw:
    # Normalize to digits only
    digits = re.sub(r'\D', '', p)
    if len(digits) >= 10:
        ALREADY_CONTACTED_PHONES.add(digits[-10:])  # Last 10 digits
print(f"Already contacted phones to exclude: {len(ALREADY_CONTACTED_PHONES)}")

# Load existing place_ids for dedup
existing_ids = set()
enriched_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lakeland_businesses_enriched.csv')
with open(enriched_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row.get('place_id', '').strip()
        if pid:
            existing_ids.add(pid)
        # Also dedup by name+address
        key = f"{row.get('name','')}-{row.get('address','')}"
        existing_ids.add(key)

print(f"Existing businesses (dedup set): {len(existing_ids)}")

# Search terms designed to find NEW businesses not in current data
# Focus on broader terms, nearby areas, and underrepresented categories
SEARCH_TERMS = [
    # Broader business types
    "business near Lakeland FL",
    "services in Lakeland FL",
    "shop in Lakeland FL",
    "store in Lakeland FL",
    "company in Lakeland FL",
    # Professional services
    "attorney Lakeland FL",
    "doctor Lakeland FL",
    "clinic Lakeland FL",
    "medical office Lakeland FL",
    "dental office Lakeland FL",
    "eye care Lakeland FL",
    "pediatrician Lakeland FL",
    "urgent care center Lakeland FL",
    "family practice Lakeland FL",
    "therapy office Lakeland FL",
    "counseling Lakeland FL",
    "psychiatrist Lakeland FL",
    # Home services
    "home improvement Lakeland FL",
    "contractor Lakeland FL",
    "renovation Lakeland FL",
    "kitchen remodel Lakeland FL",
    "bathroom remodel Lakeland FL",
    "window replacement Lakeland FL",
    "door installation Lakeland FL",
    "cabinet maker Lakeland FL",
    "custom closets Lakeland FL",
    "blinds and shutters Lakeland FL",
    "awning Lakeland FL",
    "patio Lakeland FL",
    "deck builder Lakeland FL",
    "screen enclosure Lakeland FL",
    "hurricane shutters Lakeland FL",
    # Auto
    "auto dealer Lakeland FL",
    "motorcycle shop Lakeland FL",
    "boat dealer Lakeland FL",
    "RV dealer Lakeland FL",
    "auto parts Lakeland FL",
    "transmission shop Lakeland FL",
    "muffler shop Lakeland FL",
    "alignment shop Lakeland FL",
    "car stereo Lakeland FL",
    "window tint Lakeland FL",
    # Food & entertainment
    "cafe Lakeland FL",
    "bistro Lakeland FL",
    "brewery Lakeland FL",
    "winery Lakeland FL",
    "tapas Lakeland FL",
    "catering Lakeland FL",
    "food delivery Lakeland FL",
    "event planning Lakeland FL",
    "entertainment Lakeland FL",
    "bowling alley Lakeland FL",
    "arcade Lakeland FL",
    "escape room Lakeland FL",
    "movie theater Lakeland FL",
    "karaoke Lakeland FL",
    "nightclub Lakeland FL",
    # Beauty & wellness
    "beauty salon Lakeland FL",
    "waxing Lakeland FL",
    "eyelash extensions Lakeland FL",
    "microblading Lakeland FL",
    "aesthetician Lakeland FL",
    "wellness center Lakeland FL",
    "acupuncture Lakeland FL",
    "nutritionist Lakeland FL",
    "personal trainer Lakeland FL",
    "weight loss Lakeland FL",
    # Retail
    "gift shop Lakeland FL",
    "home decor Lakeland FL",
    "antique shop Lakeland FL",
    "art gallery Lakeland FL",
    "craft store Lakeland FL",
    "toy store Lakeland FL",
    "book store Lakeland FL",
    "record store Lakeland FL",
    "sports equipment Lakeland FL",
    "outdoor gear Lakeland FL",
    "garden center Lakeland FL",
    "nursery plants Lakeland FL",
    # Financial & business
    "bank Lakeland FL",
    "credit union Lakeland FL",
    "investment advisor Lakeland FL",
    "payroll service Lakeland FL",
    "staffing agency Lakeland FL",
    "temp agency Lakeland FL",
    "marketing agency Lakeland FL",
    "web design Lakeland FL",
    "IT support Lakeland FL",
    "computer repair Lakeland FL",
    "copy center Lakeland FL",
    "sign shop Lakeland FL",
    # Education & childcare
    "school Lakeland FL",
    "academy Lakeland FL",
    "after school program Lakeland FL",
    "summer camp Lakeland FL",
    "art class Lakeland FL",
    "swim lessons Lakeland FL",
    "gymnastics Lakeland FL",
    # Pet services
    "kennel Lakeland FL",
    "pet boarding Lakeland FL",
    "pet sitting Lakeland FL",
    "dog walking Lakeland FL",
    "pet adoption Lakeland FL",
    # Nearby area expansion (same services, different spots)
    "business near Plant City FL",
    "business near Bartow FL",
    "business near Winter Haven FL",
    "business near Auburndale FL",
    "business near Mulberry FL",
    "restaurant Bartow FL",
    "restaurant Winter Haven FL",
    "contractor Winter Haven FL",
    "contractor Bartow FL",
    "hair salon Winter Haven FL",
    "dentist Winter Haven FL",
    "auto repair Bartow FL",
    "plumber Winter Haven FL",
    "electrician Bartow FL",
    "landscaping Winter Haven FL",
    "pest control Bartow FL",
    "restaurant Auburndale FL",
    "home services Mulberry FL",
]

def search_places(query, page_token=None):
    """Search Google Places Text Search API"""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_KEY}
    if page_token:
        params = {"pagetoken": page_token, "key": GOOGLE_KEY}
    
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    
    if data.get("status") not in ["OK", "ZERO_RESULTS"]:
        print(f"  API Error: {data.get('status')} - {data.get('error_message','')[:100]}")
    
    return data.get("results", []), data.get("next_page_token")

def get_place_details(place_id):
    """Get phone and website from Place Details API"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,type",
        "key": GOOGLE_KEY
    }
    r = requests.get(url, params=params, timeout=15)
    result = r.json().get("result", {})
    return {
        "phone": result.get("formatted_phone_number", ""),
        "website": result.get("website", ""),
        "types": result.get("types", [])
    }

def main():
    new_businesses = []
    seen_ids = set(existing_ids)
    total_api_calls = 0
    
    for i, query in enumerate(SEARCH_TERMS):
        print(f"\n[{i+1}/{len(SEARCH_TERMS)}] Searching: {query}")
        
        try:
            # Page 1
            results, next_token = search_places(query)
            total_api_calls += 1
            
            for r in results:
                pid = r.get("place_id", "")
                name = r.get("name", "")
                addr = r.get("formatted_address", "")
                key = f"{name}-{addr}"
                
                if pid in seen_ids or key in seen_ids:
                    continue
                
                seen_ids.add(pid)
                seen_ids.add(key)
                
                # Get category from types
                types = r.get("types", [])
                category = types[0].replace("_", " ").title() if types else query.split(" in ")[0].split(" near ")[0].strip()
                
                new_businesses.append({
                    "name": name,
                    "address": addr,
                    "category": category,
                    "phone": "",  # Will get from details
                    "website": "",
                    "email": "",
                    "rating": r.get("rating", ""),
                    "total_ratings": r.get("user_ratings_total", ""),
                    "place_id": pid
                })
            
            found_this_query = len([b for b in new_businesses if b["place_id"] not in existing_ids])
            print(f"  Page 1: {len(results)} results, {len(new_businesses)} total new")
            
            # Pages 2 and 3
            for page in [2, 3]:
                if not next_token:
                    break
                time.sleep(2)  # Google requires delay before using next_page_token
                results, next_token = search_places(query, next_token)
                total_api_calls += 1
                
                for r in results:
                    pid = r.get("place_id", "")
                    name = r.get("name", "")
                    addr = r.get("formatted_address", "")
                    key = f"{name}-{addr}"
                    
                    if pid in seen_ids or key in seen_ids:
                        continue
                    
                    seen_ids.add(pid)
                    seen_ids.add(key)
                    
                    types = r.get("types", [])
                    category = types[0].replace("_", " ").title() if types else query.split(" in ")[0].split(" near ")[0].strip()
                    
                    new_businesses.append({
                        "name": name,
                        "address": addr,
                        "category": category,
                        "phone": "",
                        "website": "",
                        "email": "",
                        "rating": r.get("rating", ""),
                        "total_ratings": r.get("user_ratings_total", ""),
                        "place_id": pid
                    })
                
                print(f"  Page {page}: {len(results)} results, {len(new_businesses)} total new")
            
            # Check if we've hit 2500+ new businesses
            if len(new_businesses) >= 2500:
                print(f"\n{'='*50}")
                print(f"HIT TARGET: {len(new_businesses)} new businesses found!")
                break
                
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    print(f"\n{'='*50}")
    print(f"SCRAPING COMPLETE")
    print(f"  New businesses found: {len(new_businesses)}")
    print(f"  API calls made: {total_api_calls}")
    
    # Get phone numbers for new businesses (batch - do top 1000)
    print(f"\nFetching phone numbers (top 1000 businesses)...")
    phone_count = 0
    for j, biz in enumerate(new_businesses[:1000]):
        try:
            details = get_place_details(biz["place_id"])
            biz["phone"] = details["phone"]
            biz["website"] = details["website"]
            total_api_calls += 1
            
            if details["phone"]:
                phone_count += 1
            
            if (j+1) % 100 == 0:
                print(f"  Details: {j+1}/1000 | phones found: {phone_count}")
                
            time.sleep(0.1)  # Slight delay
        except Exception as e:
            if "OVER_QUERY_LIMIT" in str(e) or "quota" in str(e).lower():
                print(f"  API quota hit at {j+1}. Stopping details fetch.")
                break
            continue
    
    print(f"  Phones found: {phone_count}")
    
    # Save expansion CSV
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lakeland_expansion.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name','address','category','phone','website','email','rating','total_ratings','place_id'])
        writer.writeheader()
        writer.writerows(new_businesses)
    
    print(f"\nSaved to: {output_path}")
    
    # Generate voice drop CSV (top 500 with phone numbers, excluding already contacted)
    with_phones = []
    for b in new_businesses:
        if not b.get("phone"):
            continue
        phone_digits = re.sub(r'\D', '', b["phone"])
        if len(phone_digits) >= 10 and phone_digits[-10:] not in ALREADY_CONTACTED_PHONES:
            with_phones.append(b)
    
    voicedrop_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sly_voicedrop_500.csv')
    with open(voicedrop_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Phone', 'Business Name', 'Category', 'Address'])
        for biz in with_phones[:500]:
            writer.writerow([biz['phone'], biz['name'], biz['category'], biz['address']])
    
    print(f"Voice drop CSV: {voicedrop_path} ({min(len(with_phones), 500)} leads)")
    
    # Save summary
    summary = f"""EXPANSION RESULTS:
New businesses found: {len(new_businesses)}
With phone numbers: {phone_count}
Voice drop CSV: {min(len(with_phones), 500)} leads
API calls: {total_api_calls}
Original: 3321
New total: {3321 + len(new_businesses)}
"""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expansion_result.txt'), 'w') as f:
        f.write(summary)
    
    print(f"\n{summary}")

if __name__ == "__main__":
    main()
