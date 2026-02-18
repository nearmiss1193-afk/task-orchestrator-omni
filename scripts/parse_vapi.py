import json

f = open('scripts/vapi_assistants.txt', 'r', encoding='utf-8')
data = json.load(f)
f.close()

out = []
for a in data:
    name = a.get("name", "unnamed")
    aid = a["id"]
    voice = "n/a"
    if isinstance(a.get("voice"), dict):
        voice = a["voice"].get("voiceId", "n/a")[:25]
    model = "n/a"
    if isinstance(a.get("model"), dict):
        model = a["model"].get("model", "n/a")[:25]
    phone = ""
    if a.get("phoneNumberId"):
        phone = a["phoneNumberId"]
    
    out.append(f"{name} | {aid} | voice={voice} | model={model} | phone={phone}")

f2 = open('scripts/vapi_list.md', 'w', encoding='utf-8')
f2.write("\n".join(out))
f2.close()
print(f"Wrote {len(out)} assistants")
