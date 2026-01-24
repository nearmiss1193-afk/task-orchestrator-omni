import modal
import os

app = modal.App("inspect-secrets")
SECRETS = [modal.Secret.from_name("agency-vault")]

@app.function(secrets=SECRETS)
def inspect():
    keys = list(os.environ.keys())
    print(f"AVAILABLE KEYS: {keys}")
    # Check for direct SQL access keys
    stripe_keys = [k for k in keys if "STRIPE" in k]
    return {"keys": keys, "stripe": stripe_keys}

@app.local_entrypoint()
def main():
    res = inspect.remote()
    print(f"\n[RESULTS] Found keys count: {len(res['keys'])}")
    with open("cloud_secrets_dump.txt", "w") as f:
        for k in res['keys']:
            f.write(f"{k}\n")
    print("Dumped keys to cloud_secrets_dump.txt")
