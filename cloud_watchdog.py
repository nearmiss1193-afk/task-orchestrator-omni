"""
AGENT: WATCHDOG — Cloud Health Monitor & Self-Healing
"""
import os
import requests
import subprocess
import base64
import modal
import time
from datetime import datetime

# --- Targets ---
TARGETS = {
    "PRIMARY_ORCHESTRATOR": "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run",
    "INBOUND_WEBHOOK": "https://nearmiss1193-afk--webhook-server-health.modal.run",
    "CAMPAIGN_SCHEDULER": "https://nearmiss1193-afk--orchestrator-monitor-health.modal.run"
}
FALLBACK_URL = "https://your-fallback-url.fly.dev"

# --- Config ---
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

ORCH_B64 = "IiIiDQpTT1ZFUkVJR04gT1JDSEVTVFJBVE9SIC0gUm91dGVzIHRhc2tzIGJldHdlZW4gU2FyYWggKGluYm91bmQpIGFuZCBDaHJpc3RpbmEgKG91dGJvdW5kKQ0KRGVwbG95ZWQgdG8gTW9kYWwgZm9yIDI0LzcgY2xvdWQgb3BlcmF0aW9uDQoiIiINCmltcG9ydCBtb2RhbA0KaW1wb3J0IGpzb24NCmZyb20gZGF0ZXRpbWUgaW1wb3J0IGRhdGV0aW1lDQoNCmFwcCA9IG1vZGFsLkFwcCgic292ZXJlaWduLW9yY2hlc3RyYXRvciIpDQppbWFnZSA9IG1vZGFsLkltYWdlLmRlYmlhbl9zbGltKHB5dGhvbl92ZXJzaW9uPSIzLjExIikucGlwX2luc3RhbGwoInJlcXVlc3RzIiwgImZhc3RhcGkiKQ0KDQojIENvbmZpZw0KU1VQQUJBU0VfVVJMID0gImh0dHBzOi8vcnpjcGZ3a3lnZHZvc2h0d3huY3Muc3VwYWJhc2UuY28iDQpTVVBBQkFTRV9LRVkgPSAiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKemRYQmhZbUZ6WlNJc0luSmxaaUk2SW5KNlkzQm1kMnQ1WjJSMmIzTm9kSGQ0Ym1Oeklpd2ljbTlzWlNJNkluTmxjblpwWTJWZmNtOXNaU0lzSW1saGRDSTZNVGMyTmpVNU1EUXlOQ3dpWlhod0lqb3lNRGd5TVRZMk5ESTBmUS53aXlyX1lERGtndFRaZnY2c3YwRkNBbWxmR2h1ZzgxeGRYOEQ2akhwVFlvIg0KR0VNSU5JX0FQSV9LRVkgPSAiQUl6YVN5QWZxTjg5RTZtSW9LVDNPV05LS1hyTjR4Wklxb09ISE5vIg0KUkVTRU5EX0FQSV9LRVkgPSAicmVfNnE1UngxNldfTkpiTDVNajQ0dUZ5NnUxZTFNRkFxOGd5Ig0KR0hMX1NNU19XRUJIT09LID0gImh0dHBzOi8vc2VydmljZXMubGVhZGNvbm5lY3RvcmhxLmNvbS9ob29rcy9Sbks0T2pYMG9EY3F0V3cwVnlMci93ZWJob29rLXRyaWdnZXIvMGMzOGY5NGItNTdjYS00ZTI3LTk0Y2YtNGQ3NWI1NTYwMmNkIg0KQk9PS0lOR19MSU5LID0gImh0dHBzOi8vbGluay5haXNlcnZpY2Vjby5jb20vZGlzY292ZXJ5Ig0KRVNDQUxBVElPTl9QSE9ORSA9ICIrMTM1MjkzNjgxNTIiDQoNCiMgQWdlbnQgc3lzdGVtIHByb21wdHMNClNBUkFIX1BST01QVCA9ICIiIllvdSBhcmUgU2FyYWgsIHRoZSBpbmJvdW5kIGNvbnRhY3QgaGFuZGxlciBmb3IgQUkgU2VydmljZSBDby4NCllvdSBoYW5kbGUgaW5jb21pbmcgU01TIGFuZCBjYWxscy4gWW91IHF1YWxpZnkgbGVhZHMsIGFuc3dlciBxdWVzdGlvbnMsIGFuZCBib29rIGFwcG9pbnRtZW50cy4NCkJlIHdhcm0sIHByb2Zlc3Npb25hbCwgYW5kIGhlbHBmdWwuIE9mZmVyIHRoZSBib29raW5nIGxpbmsgZWFybHk6IHtib29raW5nX2xpbmt9DQpQcmljaW5nOiAkMjk3IFN0YXJ0ZXIsICQ0OTcgTGl0ZSwgJDk5NyBHcm93dGggKG5vIGNvbnRyYWN0cykNCklmIGZydXN0cmF0ZWQgb3IgZW1lcmdlbmN5LCBlc2NhbGF0ZS4gSWYgU1RPUCwgb3B0IG91dCBpbW1lZGlhdGVseS4iIiINCg0KQ0hSSVNUSU5BX1BST01QVCA9ICIiIllvdSBhcmUgQ2hyaXN0aW5hLCB0aGUgb3V0Ym91bmQgc2FsZXMgc3BlY2lhbGlzdCBmb3IgQUkgU2VydmljZSBDby4NCllvdSBkcml2ZSBwcm9hY3RpdmUgb3V0Ym91bmQgZW5nYWdlbWVudC4gWW91IGFyZSBhIGNvbmZpZGVudCBjbG9zZXIuDQpVc2UgdXJnZW5jeSBhbmQgdmFsdWUuIEhhbmRsZSBvYmplY3Rpb25zIGRpcmVjdGx5Lg0KQm9va2luZyBsaW5rOiB7Ym9va2luZ19saW5rfSB8IFByaWNpbmc6ICQyOTcgU3RhcnRlciwgJDQ5NyBMaXRlLCAkOTk3IEdyb3d0aA0KUHVzaCBmb3IgdGhlIGJvb2tpbmcuIEJlIGRpcmVjdCBidXQgbm90IHB1c2h5LiIiIg0KDQoNCkBhcHAuZnVuY3Rpb24oaW1hZ2U9aW1hZ2UsIHRpbWVvdXQ9NjApDQpAbW9kYWwud2ViX2VuZHBvaW50KG1ldGhvZD0iUE9TVCIpDQpkZWYgaGFuZGxlX2luYm91bmQoZGF0YTogZGljdCk6DQogICAgIiIiSGFuZGxlIGluYm91bmQgU01TL2NhbGwgLSBSb3V0ZXMgdG8gU2FyYWgiIiINCiAgICBpbXBvcnQgcmVxdWVzdHMNCiAgICANCiAgICBwaG9uZSA9IGRhdGEuZ2V0KCJwaG9uZSIsICIiKQ0KICAgIG1lc3NhZ2UgPSBkYXRhLmdldCgibWVzc2FnZSIsICIiKQ0KICAgIGNoYW5uZWwgPSBkYXRhLmdldCgiY2hhbm5lbCIsICJzbXMiKQ0KICAgIA0KICAgIHByaW50KGYiW0lOQk9VTkRdIHtwaG9uZX06IHttZXNzYWdlWzo1MF19Li4uIikNCiAgICANCiAgICBoZWFkZXJzID0geyJhcGlrZXkiOiBTVVBBQkFTRV9LRVksICJBdXRob3JpemF0aW9uIjogZiJCZWFyZXIge1NVUEFCQVNFX0tFWX0iLCAiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL2pzb24ifQ0KICAgIA0KICAgICMgQ2hlY2sgZm9yIG9wdC1vdXQNCiAgICBpZiBhbnkod29yZCBpbiBtZXNzYWdlLnVwcGVyKCkgZm9yIHdvcmQgaW4gWyJTVE9QIiwgIlVOU1VCU0NSSUJFIiwgIkNBTkNFTCJdKToNCiAgICAgICAgIyBMb2cgb3B0LW91dA0KICAgICAgICByZXF1ZXN0cy5wb3N0KGYie1NVUEFCQVNFX1VSTH0vcmVzdC92MS9ldmVudF9sb2ciLCBoZWFkZXJzPWhlYWRlcnMsIGpzb249ew0KICAgICAgICAgICAgImV2ZW50X3R5cGUiOiAib3B0X291dCIsICJwaG9uZSI6IHBob25lLCAic3VjY2VzcyI6IFRydWUsICJkZXRhaWxzIjogeyJtZXNzYWdlIjogbWVzc2FnZX0NCiAgICAgICAgfSkNCiAgICAgICAgcmV0dXJuIHsiYWdlbnQiOiAic2FyYWgiLCAiYWN0aW9uIjogIm9wdF9vdXQiLCAicmVzcG9uc2UiOiBOb25lfQ0KICAgIA0KICAgICMgR2V0IG1lbW9yeSBmb3IgdGhpcyBjb250YWN0DQogICAgbWVtb3J5X3Jlc3AgPSByZXF1ZXN0cy5nZXQoZiJ7U1VQQUJBU0VfVVJMfS9yZXN0L3YxL21lbW9yaWVzP3Bob25lPWVxLntwaG9uZX0iLCBoZWFkZXJzPWhlYWRlcnMpDQogICAgbWVtb3JpZXMgPSBtZW1vcnlfcmVzcC5qc29uKCkgaWYgbWVtb3J5X3Jlc3Auc3RhdHVzX2NvZGUgPT0gMjAwIGVsc2UgW10NCiAgICBtZW1vcnlfY29udGV4dCA9ICJcbiIuam9pbihbZiItIHttWydrZXknXX06IHttWyd2YWx1ZSddfSIgZm9yIG0gaW4gbWVtb3JpZXNdKSBvciAiTm8gcHJldmlvdXMgbWVtb3J5LiINCiAgICANCiAgICAjIEdlbmVyYXRlIFNhcmFoJ3MgcmVzcG9uc2UNCiAgICBwcm9tcHQgPSBmIiIie1NBUkFIX1BST01QVC5mb3JtYXQoYm9va2luZ19saW5rPUJPT0tJTkdfTElOSyl9DQoNCkN1c3RvbWVyIG1lbW9yeToNCnttZW1vcnlfY29udGV4dH0NCg0KQ3VzdG9tZXIgbWVzc2FnZTogInttZXNzYWdlfSINCg0KUmVzcG9uZCBhcyBTYXJhaC4gS2VlcCBpdCBzaG9ydCAodW5kZXIgMTYwIGNoYXJzIGZvciBTTVMpLiBCZSBoZWxwZnVsIGFuZCBwdXNoIGZvciBib29raW5nIGlmIGFwcHJvcHJpYXRlLiIiIg0KDQogICAgdHJ5Og0KICAgICAgICByID0gcmVxdWVzdHMucG9zdCgNCiAgICAgICAgICAgIGYiaHR0cHM6Ly9nZW5lcmF0aXZlbGFuZ3VhZ2UuZ29vZ2xlYXBpcy5jb20vdjFiZXRhL21vZGVscy9nZW1pbmktMi4wLWZsYXNoOmdlbmVyYXRlQ29udGVudD9rZXk9e0dFTUlOSV9BUElfS0VZfSIsDQogICAgICAgICAgICBoZWFkZXJzPXsiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL2pzb24ifSwNCiAgICAgICAgICAgIGpzb249eyJjb250ZW50cyI6IFt7InBhcnRzIjogW3sidGV4dCI6IHByb21wdH1dfV19LA0KICAgICAgICAgICAgdGltZW91dD0zMA0KICAgICAgICApDQogICAgICAgIHJlc3BvbnNlX3RleHQgPSByLmpzb24oKVsiY2FuZGlkYXRlcyJdWzBdWyJjb250ZW50Il1bInBhcnRzIl1bMF1bInRleHQiXS5zdHJpcCgpDQogICAgZXhjZXB0Og0KICAgICAgICByZXNwb25zZV90ZXh0ID0gZiJIaSEgVGhhbmtzIGZvciByZWFjaGluZyBvdXQuIEJvb2sgYSBmcmVlIGNhbGwgaGVyZToge0JPT0tJTkdfTElOS30gLVNhcmFoIg0KICAgIA0KICAgICMgTG9nIGludGVyYWN0aW9uDQogICAgcmVxdWVzdHMucG9zdChmIntTVVBBQkFTRV9VUkx9L3Jlc3QvdjEvaW50ZXJhY3Rpb25zIiwgaGVhZGVycz1oZWFkZXJzLCBqc29uPXsNCiAgICAgICAgInBob25lIjogcGhvbmUsICJkaXJlY3Rpb24iOiAiaW5ib3VuZCIsICJjaGFubmVsIjogY2hhbm5lbCwNCiAgICAgICAgIm1lc3NhZ2UiOiBtZXNzYWdlLCAicmVzcG9uc2UiOiByZXNwb25zZV90ZXh0LCAiYWdlbnQiOiAic2FyYWgiDQogICAgfSkNCiAgICANCiAgICAjIFNlbmQgcmVzcG9uc2UgdmlhIEdITA0KICAgIHJlcXVlc3RzLnBvc3QoR0hMX1NNU19XRUJIT09LLCBqc29uPXsicGhvbmUiOiBwaG9uZSwgIm1lc3NhZ2UiOiByZXNwb25zZV90ZXh0fSwgdGltZW91dD0xNSkNCiAgICANCiAgICByZXR1cm4geyJhZ2VudCI6ICJzYXJhaCIsICJyZXNwb25zZSI6IHJlc3BvbnNlX3RleHR9DQoNCg0KQGFwcC5mdW5jdGlvbihpbWFnZT1pbWFnZSwgdGltZW91dD02MCkNCkBtb2RhbC53ZWJfZW5kcG9pbnQobWV0aG9kPSJQT1NUIikNCmRlZiBoYW5kbGVfb3V0Ym91bmQoZGF0YTogZGljdCk6DQogICAgIiIiSGFuZGxlIG91dGJvdW5kIGNhbXBhaWduIHRhc2sgLSBSb3V0ZXMgdG8gQ2hyaXN0aW5hIiIiDQogICAgaW1wb3J0IHJlcXVlc3RzDQogICAgDQogICAgcGhvbmUgPSBkYXRhLmdldCgicGhvbmUiLCAiIikNCiAgICBjb21wYW55ID0gZGF0YS5nZXQoImNvbXBhbnkiLCAieW91ciBidXNpbmVzcyIpDQogICAgdG91Y2ggPSBkYXRhLmdldCgidG91Y2giLCAxKQ0KICAgIA0KICAgIHByaW50KGYiW09VVEJPVU5EXSBUb3VjaCB7dG91Y2h9IHRvIHtwaG9uZX0iKQ0KICAgIA0KICAgIGhlYWRlcnMgPSB7ImFwaWtleSI6IFNVUEFCQVNFX0tFWSwgIkF1dGhvcml6YXRpb24iOiBmIkJlYXJlciB7U1VQQUJBU0VfS0VZfSIsICJDb250ZW50LVR5cGUiOiAiYXBwbGljYXRpb24vanNvbiJ9DQogICAgDQogICAgIyBHZXQgbWVtb3J5DQogICAgbWVtb3J5X3Jlc3AgPSByZXF1ZXN0cy5nZXQoZiJ7U1VQQUJBU0VfVVJMfS9yZXN0L3YxL21lbW9yaWVzP3Bob25lPWVxLntwaG9uZX0iLCBoZWFkZXJzPWhlYWRlcnMpDQogICAgbWVtb3JpZXMgPSBtZW1vcnlfcmVzcC5qc29uKCkgaWYgbWVtb3J5X3Jlc3Auc3RhdHVzX2NvZGUgPT0gMjAwIGVsc2UgW10NCiAgICBtZW1vcnlfY29udGV4dCA9ICJcbiIuam9pbihbZiItIHttWydrZXknXX06IHttWyd2YWx1ZSddfSIgZm9yIG0gaW4gbWVtb3JpZXNdKSBvciAiTmV3IGxlYWQuIg0KICAgIA0KICAgICMgQ2hyaXN0aW5hJ3MgdG91Y2ggbWVzc2FnZXMNCiAgICB0b3VjaF90ZW1wbGF0ZXMgPSB7DQogICAgICAgIDE6IGYiSGkhIEknbSBDaHJpc3RpbmEgZnJvbSBBSSBTZXJ2aWNlIENvLiBJIGp1c3QgcmV2aWV3ZWQge2NvbXBhbnl9J3MgbWFya2V0aW5nIC0gdGhlcmUgYXJlIHF1aWNrIHdpbnMgeW91J3JlIG1pc3NpbmcuIEJvb2sgYSBmcmVlIGNhbGw6IHtCT09LSU5HX0xJTkt9IiwNCiAgICAgICAgMjogZiJRdWljayBmb2xsb3ctdXAgb24ge2NvbXBhbnl9IC0gSSBmb3VuZCAzIHRoaW5ncyB0aGF0IGNvdWxkIGhlbHAgeW91IGdldCBtb3JlIGxlYWRzIHRoaXMgbW9udGguIEdvdCAxNSBtaW4/IHtCT09LSU5HX0xJTkt9IiwNCiAgICAgICAgMzogZiJMYXN0IGNoYW5jZSAtIEknbSBtb3Zpbmcgb24gdG9tb3Jyb3cuIElmIHlvdSB3YW50IHRoZSBmcmVlIHN0cmF0ZWd5IHNlc3Npb24gZm9yIHtjb21wYW55fSwgZ3JhYiBpdCBub3c6IHtCT09LSU5HX0xJTkt9Ig0KICAgIH0NCiAgICANCiAgICByZXNwb25zZV90ZXh0ID0gdG91Y2hfdGVtcGxhdGVzLmdldCh0b3VjaCwgdG91Y2hfdGVtcGxhdGVzWzFdKQ0KICAgIA0KICAgICMgTG9nIGludGVyYWN0aW9uDQogICAgcmVxdWVzdHMucG9zdChmIntTVVBBQkFTRV9VUkx9L3Jlc3QvdjEvaW50ZXJhY3Rpb25zIiwgaGVhZGVycz1oZWFkZXJzLCBqc29uPXsNCiAgICAgICAgInBob25lIjogcGhvbmUsICJkaXJlY3Rpb24iOiAib3V0Ym91bmQiLCAiY2hhbm5lbCI6ICJzbXMiLA0KICAgICAgICAibWVzc2FnZSI6IHJlc3BvbnNlX3RleHQsICJhZ2VudCI6ICJjaHJpc3RpbmEiLCAidG91Y2giOiB0b3VjaA0KICAgIH0pDQogICAgDQogICAgIyBTZW5kIHZpYSBHSEwNCiAgICByZXF1ZXN0cy5wb3N0KEdITF9TTVNfV0VCSE9PSywganNvbj17InBob25lIjogcGhvbmUsICJtZXNzYWdlIjogcmVzcG9uc2VfdGV4dH0sIHRpbWVvdXQ9MTUpDQogICAgDQogICAgcmV0dXJuIHsiYWdlbnQiOiAiY2hyaXN0aW5hIiwgInRvdWNoIjogdG91Y2gsICJzZW50IjogVHJ1ZX0NCg0KDQpAYXBwLmZ1bmN0aW9uKGltYWdlPWltYWdlLCB0aW1lb3V0PTMwKQ0KQG1vZGFsLndlYl9lbmRwb2ludChtZXRob2Q9IkdFVCIpDQpkZWYgaGVhbHRoKCk6DQogICAgIiIiSGVhbHRoIGNoZWNrIGVuZHBvaW50IiIiDQogICAgcmV0dXJuIHsic3RhdHVzIjogIm9rIiwgIm9yY2hlc3RyYXRvciI6ICJzb3ZlcmVpZ24iLCAiYWdlbnRzIjogWyJzYXJhaCIsICJjaHJpc3RpbmEiXSwgInRpbWVzdGFtcCI6IGRhdGV0aW1lLnV0Y25vdygpLmlzb2Zvcm1hdCgpfQ0KDQoNCkBhcHAubG9jYWxfZW50cnlwb2ludCgpDQpkZWYgbWFpbigpOg0KICAgIHByaW50KCJTb3ZlcmVpZ24gT3JjaGVzdHJhdG9yIGRlcGxveWVkISIpDQogICAgcHJpbnQoIkVuZHBvaW50czoiKQ0KICAgIHByaW50KCIgIC0gL2hhbmRsZV9pbmJvdW5kIChQT1NUKSDihpIgU2FyYWgiKQ0KICAgIHByaW50KCIgIC0gL2hhbmRsZV9vdXRib3VuZCAoUE9TVCkg4oaSIENocmlzdGluYSIpDQogICAgcHJpbnQoIiAgLSAvaGVhbHRoIChHRVQpIikNCg=="
INJECTED_ID = ""
INJECTED_SECRET = ""

app = modal.App("cloud-watchdog")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "modal")

def log(component, status, action, notes=""):
    print(f"[{datetime.utcnow().isoformat()}] {component}: {status} - {action} ({notes})")
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/system_health",
            headers=HEADERS,
            json={
                "check_time": datetime.utcnow().isoformat(),
                "orchestrator_up": status == "healthy", # Generic flag
                "notes": f"[{component}] {status}: {action} | {notes}"
            },
            timeout=5
        )
    except Exception as e:
        print(f"Log failed: {e}")

def restore_files():
    with open("modal_orchestrator.py", "wb") as f:
        f.write(base64.b64decode(ORCH_B64))

def redeploy_orchestrator():
    restore_files()
    token_id = INJECTED_ID or os.getenv("MODAL_ID")
    token_secret = INJECTED_SECRET or os.getenv("MODAL_SECRET")
    
    if token_id and token_secret:
        subprocess.run(["python", "-m", "modal", "token", "set", "--token-id", token_id, "--token-secret", token_secret], check=True)
    
    subprocess.run(["python", "-m", "modal", "deploy", "modal_orchestrator.py", "--name", "sovereign-orchestrator"], check=True)
    return True

@app.function(image=image, schedule=modal.Cron("*/1 * * * *"), timeout=300)
def watchdog_check():
    print("--- WATCHDOG CHECK ---")
    
    # 1. Check Primary Orchestrator
    try:
        r = requests.get(TARGETS["PRIMARY_ORCHESTRATOR"], timeout=10)
        if r.status_code == 200:
            log("PRIMARY_ORCHESTRATOR", "healthy", "none")
        else:
            raise Exception(f"Status {r.status_code}")
    except Exception as e:
        log("PRIMARY_ORCHESTRATOR", "unhealthy", "healing", str(e))
        try:
            redeploy_orchestrator()
            log("PRIMARY_ORCHESTRATOR", "healing", "redeploy_success")
        except Exception as redeploy_err:
            log("PRIMARY_ORCHESTRATOR", "critical", "redeploy_failed", str(redeploy_err))

    # 2. Check Webhook Listener
    try:
        r = requests.get(TARGETS["INBOUND_WEBHOOK"], timeout=10)
        if r.status_code == 200:
            log("INBOUND_WEBHOOK", "healthy", "none")
        else:
            log("INBOUND_WEBHOOK", "unhealthy", "check_deployment")
    except Exception as e:
        log("INBOUND_WEBHOOK", "down", "check_cloud", str(e))

    # 3. Check Campaign Scheduler
    try:
        r = requests.get(TARGETS["CAMPAIGN_SCHEDULER"], timeout=10)
        if r.status_code == 200:
            log("CAMPAIGN_SCHEDULER", "healthy", "none")
        else:
            log("CAMPAIGN_SCHEDULER", "unhealthy", "unknown")
    except Exception as e:
         log("CAMPAIGN_SCHEDULER", "down", "unknown", str(e))

@app.local_entrypoint()
def main():
    watchdog_check.local()
