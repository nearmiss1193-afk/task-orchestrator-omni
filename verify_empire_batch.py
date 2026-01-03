import sys
import os

# Mock Imports for Bulk Verification
try:
    from modules.web.electrician_landing import get_electrician_landing_html
    from modules.web.solar_landing import get_solar_landing_html
    from modules.web.landscaping_landing import get_landscaping_landing_html
    from modules.web.pest_landing import get_pest_landing_html
    from modules.web.cleaning_landing import get_cleaning_landing_html
    from modules.web.restoration_landing import get_restoration_landing_html
    from modules.web.autodetail_landing import get_autodetail_landing_html
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def verify_all():
    print("🌍 Verifying Empire Expansion (Industries 4-10)...")
    
    modules = [
        ("Electrician", get_electrician_landing_html, "Electrician Ellie"),
        ("Solar", get_solar_landing_html, "Sunny Sam"),
        ("Landscaping", get_landscaping_landing_html, "Green Thumb Gary"),
        ("Pest Control", get_pest_landing_html, "Exterminator Ed"),
        ("Cleaning", get_cleaning_landing_html, "Maid Mary"),
        ("Restoration", get_restoration_landing_html, "Flood Phil"),
        ("Auto Detail", get_autodetail_landing_html, "Detail Dave"),
    ]
    
    success_count = 0
    
    for name, func, keyword in modules:
        try:
            html = func()
            if keyword in html and "Vapi" in html:
                print(f"✅ {name}: Validated ({keyword})")
                success_count += 1
            else:
                print(f"❌ {name}: HTML Generation Failed or Missing Keywords")
        except Exception as e:
             print(f"❌ {name}: Execution Error {e}")
             
    print(f"\nStatus: {success_count}/{len(modules)} Ready for Launch.")

if __name__ == "__main__":
    verify_all()
