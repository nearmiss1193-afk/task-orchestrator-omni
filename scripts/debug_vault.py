import modal
import os

app = modal.App("debug-vault")
VAULT = modal.Secret.from_name("sovereign-vault")

@app.function(secrets=[VAULT])
def check_vars():
    print("🔑 Env Var Keys in Sovereign Vault:")
    keys = sorted(list(os.environ.keys()))
    for k in keys:
        if any(term in k.upper() for term in ["VAPI", "KEY", "SECRET", "AUTH"]):
            # Just print the key name, not the value!
            print(f" - {k}")

if __name__ == "__main__":
    with app.run():
        check_vars.remote()
