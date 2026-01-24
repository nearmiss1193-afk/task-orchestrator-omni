
import os

print("🔍 CHECKING LOCAL ENV...")
for k, v in os.environ.items():
    if "STRIPE" in k or "sk_" in v:
        print(f"FOUND IN ENV: {k} = {v[:10]}...")
