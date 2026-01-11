"""
TEST ENRICHMENT WITH LARGE COMPANIES
Verify Hunter/Apollo APIs work with well-known companies
"""
from enrich_decision_makers import enrich_lead

# Test with large, well-known companies that should be in the databases
test_companies = [
    "Salesforce",
    "HubSpot", 
    "Stripe",
    "Zoom",
    "Slack"
]

print("="*60)
print("TESTING ENRICHMENT WITH LARGE COMPANIES")
print("="*60)

results = []
for company in test_companies:
    print(f"\n{'='*60}")
    result = enrich_lead(company)
    results.append((company, result))
    print()

print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)

success = sum(1 for _, r in results if r is not None)
print(f"\nSuccess Rate: {success}/{len(results)} ({success/len(results)*100:.0f}%)")

for company, result in results:
    if result:
        print(f"✅ {company}: {result.get('name')} - {result.get('email')} - {result.get('source')}")
    else:
        print(f"❌ {company}: No info found")

print("\n" + "="*60)
if success > 0:
    print("✅ APIs ARE WORKING - Issue is small local companies not in database")
    print("\nRECOMMENDATION:")
    print("1. For small HVAC companies: Use main line (current approach)")
    print("2. For larger prospects: Use enrichment")
    print("3. Consider manual research for high-value targets")
else:
    print("❌ APIs NOT WORKING - Check API keys or rate limits")
