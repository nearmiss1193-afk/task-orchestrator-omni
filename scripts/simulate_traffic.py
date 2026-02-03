
import json
import time
import random
import os

STATE_FILE = "server_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

print("🚦 Starting Traffic Simulation...")
print(f"Monitoring: {STATE_FILE}")
print("Watch the Dashboard Updates in Real-Time.")

# Initial Stats
revenue = 650.00
agents = 12
notifications = 3

for i in range(30): # Run for 60 seconds (2s interval)
    # Simulate variations
    revenue += random.choice([0, 0, 49.99, 150.00])
    load = random.randint(15, 45)
    
    if random.random() > 0.8:
        notifications += 1
        
    state = {
        "active_agents": agents,
        "system_load": f"{load}%",
        "revenue_today": f"${revenue:,.2f}",
        "active_campaigns": 10,
        "notifications": notifications,
        "network_status": "Traffic Spike"
    }
    
    save_state(state)
    print(f"[{i+1}/30] Revenue: ${revenue:,.2f} | Load: {load}% | Agents: {agents}")
    time.sleep(2)

print("\n🏁 Simulation Complete.")
