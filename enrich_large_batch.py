"""
ENRICH 50+ EMPLOYEE COMPANIES - Batch Processing
Uses Hunter.io + Apollo.io to enrich large HVAC companies
"""
import os
import json
import time
from dotenv import load_dotenv
from enrich_decision_makers import enrich_lead

load_dotenv()

# 50+ Employee HVAC Companies
LARGE_COMPANIES = [
    # Bay Area (10)
    {"company_name": "Service Champions", "domain": "servicechampions.net", "city": "San Jose", "state": "CA"},
    {"company_name": "Bell Brothers", "domain": "bellbrothers.com", "city": "Sacramento", "state": "CA"},
    {"company_name": "Bonney Plumbing", "domain": "bonney.com", "city": "Sacramento", "state": "CA"},
    {"company_name": "Cabrillo Plumbing", "domain": "cabrilloplumbing.com", "city": "San Francisco", "state": "CA"},
    {"company_name": "ABCO Mechanical", "domain": "abcomechanical.com", "city": "San Francisco", "state": "CA"},
    
    # Southern California (10)
    {"company_name": "Nexgen HVAC", "domain": "nexgenhvac.com", "city": "Anaheim", "state": "CA"},
    {"company_name": "Gideon Brothers HVAC", "domain": "gideonbrothers.com", "city": "Los Angeles", "state": "CA"},
    {"company_name": "Gorgis AC Heating", "domain": "gorgisac.com", "city": "San Diego", "state": "CA"},
    {"company_name": "San Diego Air Conditioning", "domain": "sdairconditioning.com", "city": "San Diego", "state": "CA"},
    {"company_name": "Ambient Heating AC", "domain": "ambientheatingac.com", "city": "San Diego", "state": "CA"},
    
    # Arizona (5)
    {"company_name": "George Brazil", "domain": "georgebrazil.com", "city": "Phoenix", "state": "AZ"},
    {"company_name": "Goettl Air Conditioning", "domain": "goettl.com", "city": "Phoenix", "state": "AZ"},
    {"company_name": "American Home Water & Air", "domain": "americanhomewater.com", "city": "Phoenix", "state": "AZ"},
    {"company_name": "Parker & Sons", "domain": "parkerandsons.com", "city": "Phoenix", "state": "AZ"},
    {"company_name": "Chas Roberts", "domain": "chasroberts.com", "city": "Phoenix", "state": "AZ"},
    
    # Nevada (3)
    {"company_name": "Precision Air & Plumbing", "domain": "precisionairlv.com", "city": "Las Vegas", "state": "NV"},
    {"company_name": "HVAC Investigators", "domain": "hvacinvestigators.com", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Air Conditioning Specialists", "domain": "air-conditioning-specialists.com", "city": "Las Vegas", "state": "NV"},
]

def enrich_batch(companies, output_file='enriched_large_companies.json'):
    """
    Enrich a batch of companies and save results
    """
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      🏢 ENRICHING {len(companies)} LARGE HVAC COMPANIES              ║
║      Using Hunter.io + Apollo.io APIs                    ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    enriched = []
    success_count = 0
    
    for i, company in enumerate(companies):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(companies)}] {company['company_name']}")
        print(f"{'='*60}")
        
        # Enrich with APIs
        result = enrich_lead(company['company_name'], company.get('domain'))
        
        # Add enrichment data to company
        if result:
            company['enriched'] = True
            company['owner_name'] = result.get('name')
            company['owner_email'] = result.get('email')
            company['owner_phone'] = result.get('phone')
            company['owner_title'] = result.get('title')
            company['enrichment_source'] = result.get('source')
            success_count += 1
            print(f"  ✅ SUCCESS: {result.get('name')} ({result.get('title')})")
        else:
            company['enriched'] = False
            print(f"  ❌ FAILED: No decision maker found")
        
        enriched.append(company)
        
        # Brief pause to avoid rate limits
        if i < len(companies) - 1:
            time.sleep(2)
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(enriched, f, indent=2)
    
    # Print summary
    success_rate = (success_count / len(companies)) * 100
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      📊 ENRICHMENT COMPLETE                              ║
║      Success: {success_count}/{len(companies)} ({success_rate:.0f}%)                                  ║
║      Saved to: {output_file}                             ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Show enriched companies
    print("\n✅ ENRICHED COMPANIES:")
    for company in enriched:
        if company.get('enriched'):
            print(f"  • {company['company_name']}: {company.get('owner_name')} - {company.get('owner_email')}")
    
    print(f"\n❌ FAILED TO ENRICH:")
    for company in enriched:
        if not company.get('enriched'):
            print(f"  • {company['company_name']}")
    
    return enriched

if __name__ == '__main__':
    enriched_companies = enrich_batch(LARGE_COMPANIES)
    
    print(f"\n\n🎯 NEXT STEPS:")
    print(f"1. Review enriched_large_companies.json")
    print(f"2. Verify contact info for enriched companies")
    print(f"3. Launch campaign using campaign_enriched.py")
    print(f"4. Track decision maker contact rate")
