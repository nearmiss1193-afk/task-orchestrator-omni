import hashlib

def get_strategy(lead_id):
    hash_obj = hashlib.md5(lead_id.encode())
    hash_val = int(hash_obj.hexdigest(), 16)
    strategy_index = hash_val % 3
    strategies = ["Casual Manus", "Authority Audit", "Vanguard Waitlist"]
    return strategies[strategy_index]

# Test with some random IDs
test_ids = [
    "c086f2ce-72f5-4f9f-b381-b94549b85c1d",
    "d444dfee-1166-461d-840b-a14ebf09c4dc",
    "4d138ed0-d86e-49f2-b214-3f44e2657285",
    "ae138ed0-d86e-49f2-b214-3f44e2657286",
    "be138ed0-d86e-49f2-b214-3f44e2657287"
]

for lid in test_ids:
    print(f"Lead ID {lid} -> Strategy: {get_strategy(lid)}")
