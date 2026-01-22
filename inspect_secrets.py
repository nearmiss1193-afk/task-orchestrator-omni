import modal
import os

app = modal.App("inspect-secrets")
SECRETS = [modal.Secret.from_name("aiserviceco-secrets"), modal.Secret.from_name("agency-vault")]

@app.function(secrets=SECRETS)
def inspect():
    keys = list(os.environ.keys())
    print(f"AVAILABLE KEYS: {keys}")
    # Check for direct SQL access keys
    sql_keys = [k for k in keys if "POSTGRES" in k or "DB" in k or "SQL" in k]
    print(f"SQL KEYS: {sql_keys}")
    return {"sql_keys": sql_keys}

@app.local_entrypoint()
def main():
    inspect.remote()
