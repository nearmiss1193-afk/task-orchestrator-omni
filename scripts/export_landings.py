
import os
import sys

# Ensure modules are in path
sys.path.append(os.getcwd())

from modules.web.hvac_landing import get_hvac_landing_html
from modules.web.plumber_landing import get_plumber_landing_html
from modules.web.roofer_landing import get_roofer_landing_html
from modules.web.electrician_landing import get_electrician_landing_html
from modules.web.solar_landing import get_solar_landing_html
from modules.web.landscaping_landing import get_landscaping_landing_html
from modules.web.pest_landing import get_pest_landing_html
from modules.web.cleaning_landing import get_cleaning_landing_html
from modules.web.restoration_landing import get_restoration_landing_html
from modules.web.autodetail_landing import get_autodetail_landing_html

EXPORT_DIR = "apps/portal/public/landing"
os.makedirs(EXPORT_DIR, exist_ok=True)

PAGES = {
    "hvac": get_hvac_landing_html(),
    "plumber": get_plumber_landing_html(),
    "roofer": get_roofer_landing_html(),
    "electrician": get_electrician_landing_html(),
    "solar": get_solar_landing_html(),
    "landscaping": get_landscaping_landing_html(),
    "pest": get_pest_landing_html(),
    "cleaning": get_cleaning_landing_html(),
    "restoration": get_restoration_landing_html(),
    "autodetail": get_autodetail_landing_html(),
}

print(f"🚀 Exporting {len(PAGES)} Landing Pages to {EXPORT_DIR}...")

for name, html in PAGES.items():
    path = f"{EXPORT_DIR}/{name}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Exported: {path}")

print("\n🎉 Export Complete. Access at https://empire-unified-backup-production.up.railway.app/landing/[name].html")
