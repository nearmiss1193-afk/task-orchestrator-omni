import os

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "[File Not Found]"

base_brain = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400"
base_scratch = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified"

dns = read_file(os.path.join(base_scratch, "DNS_RECORDS.txt"))
capabilities = read_file(os.path.join(base_brain, "EMPIRE_CAPABILITIES_MASTER.md"))
recovery = read_file(os.path.join(base_brain, "RECOVERY_PROTOCOL.md"))
roadmap = read_file(os.path.join(base_brain, "EMPIRE_EXPANSION_ROADMAP.md"))

content = f"""
================================================================================
SOVEREIGN COMMAND: FINAL HANDOFF PACKET
================================================================================
DATE: 2026-01-02
STATUS: SECURE

[CRITICAL ACTION REQUIRED]
To restore Email Communications (including "Owner Recipient" alerts), 
you MUST add the following records to your DNS Provider for 'aiserviceco.com'.

{dns}

================================================================================
DOCUMENT 1: EMPIRE CAPABILITIES MASTER
================================================================================
{capabilities}

================================================================================
DOCUMENT 2: RECOVERY PROTOCOL & OFFLINE PROCEDURES
================================================================================
{recovery}

================================================================================
DOCUMENT 3: EXPANSION ROADMAP & CHAIN OF COMMAND
================================================================================
{roadmap}

[END OF PACKET]
"""

out_path = os.path.join(base_brain, "HANDOFF_PACKET_FINAL.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Handoff Packet Assembled at: {out_path}")
