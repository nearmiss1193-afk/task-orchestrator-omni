import json

try:
    with open('modal_list.json', 'r', encoding='utf-16') as f:
        data = json.load(f)
        
    with open('zombies.txt', 'w', encoding='utf-8') as zf:
        zf.write(f"Total Apps Found: {len(data)}\n")
        zf.write("\n--- ACTIVE / DEPLOYED / EPHEMERAL APPS ---\n")
        active_count = 0
        for app in data:
            state = app.get("State", "Unknown")
            if state != "stopped" and state != "detached":
                # Only list active ones
                line = f"[{state}] ID: {app.get('App ID')} | Name: {app.get('Description', 'Unknown')} | Created: {app.get('Created at')}\n"
                print(line.strip())
                zf.write(line)
                active_count += 1
        zf.write(f"\nTotal Active Count: {active_count}\n")
    
    print(f"\nTotal Active Count: {active_count}")

except Exception as e:
    print(f"Error: {e}")
