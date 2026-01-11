# Top 20 High-Value HVAC Prospects for Manual Research

## Selection Criteria

- Multiple locations OR large service area
- Professional website
- Active online presence
- 20+ employees estimated
- Good reviews/reputation

---

## Top 20 Prospects (To Be Researched)

| # | Company Name | City | State | Phone | Est. Size | Website | Owner Name | Owner Email | Owner Phone | LinkedIn | Notes |
|---|--------------|------|-------|-------|-----------|---------|------------|-------------|-------------|----------|-------|
| 1 | Service Champions | San Jose | CA | 408-351-8757 | 300+ | servicechampions.net | | | | | Multi-location, Bay Area leader |
| 2 | Nexgen HVAC | Anaheim | CA | 714-597-4550 | 200+ | nexgenhvac.com | | | | | Southern CA, multiple locations |
| 3 | Bonney Plumbing | Sacramento | CA | 916-246-6628 | 150+ | bonney.com | | | | | Sacramento leader, 40+ years |
| 4 | George Brazil | Phoenix | AZ | 602-870-6840 | 200+ | georgebrazil.com | | | | | Phoenix market leader |
| 5 | Goettl Air Conditioning | Phoenix | AZ | 602-264-4226 | 150+ | goettl.com | | | | | Major AZ player |
| 6 | American Home Water & Air | Phoenix | AZ | 602-993-0083 | 100+ | americanhomewater.com | | | | | Growing Phoenix company |
| 7 | Precision Air & Plumbing | Las Vegas | NV | 702-553-1262 | 80+ | precisionairlv.com | | | | | Las Vegas leader |
| 8 | HVAC Investigators | Las Vegas | NV | 702-723-4704 | 60+ | hvacinvestigators.com | | | | | Vegas, good reputation |
| 9 | Gideon Brothers HVAC | Los Angeles | CA | 213-379-5931 | 75+ | gideonbrothers.com | | | | | LA multi-location |
| 10 | Cabrillo Plumbing AC | San Francisco | CA | 415-360-0560 | 50+ | cabrilloplumbing.com | | | | | SF established company |
| 11 | ABCO Mechanical | San Francisco | CA | 415-648-7135 | 60+ | abcomechanical.com | | | | | Commercial + residential |
| 12 | Same Day Heating AC | Sacramento | CA | 916-594-4500 | 40+ | samedayheating.com | | | | | Fast-growing Sacramento |
| 13 | Garick Air Conditioning | Sacramento | CA | 916-452-2477 | 50+ | garickac.com | | | | | Sacramento established |
| 14 | Roach Heating AC | Sacramento | CA | 916-605-8583 | 45+ | roachheating.com | | | | | Sacramento area |
| 15 | Steve Patrick AC | Fresno | CA | 559-224-1729 | 35+ | stevepatrickac.com | | | | | Central Valley leader |
| 16 | Gorgis AC Heating | San Diego | CA | 619-780-1104 | 40+ | gorgisac.com | | | | | San Diego established |
| 17 | San Diego Air Conditioning | San Diego | CA | 619-794-6867 | 50+ | sdairconditioning.com | | | | | SD multi-location |
| 18 | Ambient Heating AC | San Diego | CA | 619-454-4975 | 30+ | ambientheatingac.com | | | | | SD growing company |
| 19 | Standard Air Hawaii | Honolulu | HI | 808-302-0644 | 40+ | standardairhawaii.com | | | | | Hawaii market leader |
| 20 | Advanced AC Hawaii | Honolulu | HI | 808-847-4814 | 35+ | advancedachawaii.com | | | | | Honolulu established |

---

## Research Workflow

For each company above:

### Step 1: LinkedIn Search

- Search: "[Company Name] owner" OR "[Company Name] CEO"
- Look for: Founder, Owner, President, CEO profiles
- Capture: Name, title, LinkedIn URL

### Step 2: Company Website

- Check: "About Us", "Team", "Leadership" pages
- Look for: Owner/founder bio, contact info
- Capture: Name, email if listed

### Step 3: Hunter.io Lookup

```python
from enrich_decision_makers import enrich_with_hunter
result = enrich_with_hunter("Company Name", "domain.com")
```

### Step 4: Apollo.io Lookup

```python
from enrich_decision_makers import enrich_with_apollo
result = enrich_with_apollo("Company Name", "domain.com")
```

### Step 5: Manual Verification

- Google: "[Owner Name] [Company] email"
- Verify phone numbers are current
- Check LinkedIn for direct contact preferences

---

## Priority Order

**Week 1:** Research companies #1-10 (largest, highest value)
**Week 2:** Research companies #11-20

---

## Success Metrics

- **Target:** Find owner contact for 15/20 companies (75%)
- **Data Quality:** Verify email + phone for 10/20 (50%)
- **Outreach:** Contact all 20 within 2 weeks
- **Conversion:** Book 3+ demos from top 20

---

## Notes

- Focus on companies with 50+ employees first (more likely in databases)
- For smaller companies (20-50), may need more manual research
- Update this spreadsheet as research progresses
- Track which enrichment method worked (Hunter, Apollo, manual, etc.)
